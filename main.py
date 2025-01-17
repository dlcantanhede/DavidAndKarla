from datetime import datetime
from flask import jsonify
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pytz  # Importando o pytz para trabalhar com fusos horários

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dating.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo do banco de dados
class RelationshipStartDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)

# Definindo o fuso horário de São Paulo
timezone = pytz.timezone('America/Sao_Paulo')

# Rota principal
@app.route('/')
def home():
    # Obtém a data de início do relacionamento do banco de dados
    relationship = RelationshipStartDate.query.first()
    if not relationship:
        # Define uma data padrão se não houver registro no banco de dados
        relationship = RelationshipStartDate(
            start_date=timezone.localize(datetime(2022, 1, 14, 0, 0, 0))
        )
        db.session.add(relationship)
        db.session.commit()

    # Ajusta o horário da data de início para o fuso horário correto
    start_date = relationship.start_date
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=pytz.utc).astimezone(timezone)

    # Calcula o tempo de namoro
    now = datetime.now(timezone)  # Agora também deve ser no fuso horário correto
    time_difference = now - start_date

    days_together = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return render_template(
        'index.html', 
        start_date=start_date, 
        days_together=days_together, 
        hours=hours, 
        minutes=minutes, 
        seconds=seconds
    )

@app.route('/time')
def get_time():
    relationship = RelationshipStartDate.query.first()
    if not relationship:
        return jsonify(error="Data de relacionamento não encontrada"), 404

    start_date = relationship.start_date.replace(tzinfo=pytz.utc).astimezone(timezone)
    now = datetime.now(timezone)

    # Calcula a diferença com relativedelta
    delta = relativedelta(now, start_date)

    return jsonify(
        years=delta.years,
        months=delta.months,
        days=delta.days,
        hours=now.hour,
        minutes=now.minute,
        seconds=now.second
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False)
