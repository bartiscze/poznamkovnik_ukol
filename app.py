import sqlite3
# Nový import:
import os
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, length
from wtforms import TextAreaField
from wtforms import RadioField

app = Flask(__name__)
app.debug = True
app.secret_key = 'svsdfvsdfvbadb  sfgsgsrg'

# Bude důležité pro pythonanywhere.com

aktualni_adresar = os.path.abspath(os.path.dirname(__file__))
databaze = (os.path.join(aktualni_adresar, 'poznamky.db'))

class PoznamkaForm(FlaskForm):
    poznamka = TextAreaField('Poznámka', validators=[DataRequired(), length(max=250)])
    dulezitost = RadioField("Dulezitost",choices=[("1", 'málo důležitá poznámka (ŽLUTÁ)'), ("2", 'středně důležitá poznámka (MODRÁ)'), ("3", 'důležitá poznámka (ČERVENÁ)')])


@app.route('/poznamka/vlozit', methods=['GET', 'POST'])
def vloz_poznamku():
    """Zobrazí folrmulář a vloží poznámku."""
    form = PoznamkaForm()
    poznamka_text = form.poznamka.data
    dulezitost = form.dulezitost.data
    if form.validate_on_submit():
        conn = sqlite3.connect(databaze)
        c = conn.cursor()
        # Podívejte se sem!!!:
        # https://docs.python.org/3/library/sqlite3.html
        # a hledejte text: Never do this -- insecure!
        # Aby nedošlo k útoku SQL injection na vaší aplikaci:
        c.execute("INSERT INTO poznamka(telo,dulezitost) VALUES (?,?)", (poznamka_text,dulezitost,))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('vloz_poznamku.html', form=form)


@app.route('/')
def zobraz_poznamky():
    """Zobrazí všechny poznamky."""
    conn = sqlite3.connect(databaze)
    c = conn.cursor()
    # rowid je sloupec, který vytváří sqlite automaticky,
    # číslo sloupce budeme potřebovat později...
    # využijeme ho jako primární klíč.
    # viz: https://www.sqlitetutorial.net/sqlite-autoincrement/
    c.execute("SELECT rowid, telo, kdy, dulezitost FROM poznamka ORDER BY rowid DESC")
    # Chci všechno - použiju fetchall()
    poznamky = c.fetchall()
    conn.close()
    return render_template('zobraz_poznamky.html', poznamky=poznamky)


# <int:poznamka_id> definuje, že v URL bude na konci integer s id (rowid) poznámky
# Viz.: https://www.tutorialspoint.com/flask/flask_variable_rules.htm
@app.route('/smaz/<int:poznamka_id>')
def smaz_poznamku(poznamka_id):
    """Smaže vybranou poznámku"""
    conn = sqlite3.connect(databaze)
    c = conn.cursor()
    # Aby nedošlo k útoku SQL injection na vaší aplikaci! Viz. nahoře.
    c.execute("DELETE FROM poznamka WHERE rowid=?", (poznamka_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/uprav/<int:poznamka_id>', methods=['GET', 'POST'])
def uprav_poznamku(poznamka_id):
    """Upraví poznámku."""
    # Potřebujeme získat poznámku z databáze
    conn = sqlite3.connect(databaze)
    c = conn.cursor()
    # Poznámku získáme výběrem z databáze, kdy hledáme řádek s id poznámky
    c.execute("SELECT telo, kdy FROM poznamka WHERE rowid=?", (poznamka_id,))
    # Dotazem získám seznam (n-tici) s daty
    poznamka_tuple = c.fetchone()
    conn.close()
    # Naplnění formuláře daty z databáze
    form = PoznamkaForm(poznamka=poznamka_tuple[0])
    poznamka_text = form.poznamka.data
    if form.validate_on_submit():
        conn = sqlite3.connect(databaze)
        c = conn.cursor()
        # Podívejte se sem!!!:
        # https://docs.python.org/3/library/sqlite3.html
        # a hledejte text: Never do this -- insecure!
        # Aby nedošlo k útoku SQL injection na vaší aplikaci:
        c.execute("UPDATE poznamka SET telo=? WHERE rowid=?", (poznamka_text, poznamka_id,))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('vloz_poznamku.html', form=form)


if __name__ == '__main__':
    app.run()
