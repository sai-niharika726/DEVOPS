from flask import Flask, render_template, request

app = Flask(__name__)

students = [
    {
        "name": "Rahul Sharma",
        "course": "Computer Science",
        "fee_paid": 45000,
        "total_fee": 80000,
    },
    {
        "name": "Ananya Reddy",
        "course": "Electronics",
        "fee_paid": 70000,
        "total_fee": 85000,
    }
]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        fee_paid = int(request.form['fee_paid'])
        total_fee = int(request.form['total_fee'])

        students.append({
            'name': name,
            'course': course,
            'fee_paid': fee_paid,
            'total_fee': total_fee
        })

    return render_template('index.html', students=students)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
