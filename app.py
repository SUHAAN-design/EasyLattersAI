from flask import Flask, render_template_string, request
import requests
from datetime import datetime

app = Flask(__name__)

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Letter Generator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 700px; margin: auto; padding: 20px; }
        input, select, textarea { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        .letter-box { white-space: pre-wrap; background: #f9f9f9; padding: 15px; border: 1px solid #ddd; margin-top: 20px; }
        .error { color: red; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <h1>AI Letter Generator</h1>
    <form method="POST" id="letterForm" novalidate>
        <label for="name">Your Full Name: <span style="color:red">*</span></label>
        <input type="text" name="name" placeholder="Enter your full name" required value="{{ request.form.get('name', '') }}">

        <label for="your_address">Your Full Address: <span style="color:red">*</span></label>
        <textarea name="your_address" placeholder="Enter your full address" rows="3" required>{{ request.form.get('your_address', '') }}</textarea>

        <label for="email">Your Email Address (optional):</label>
        <input type="email" name="email" placeholder="Enter your email address" value="{{ request.form.get('email', '') }}">

        <label for="phone">Your Phone Number (optional):</label>
        <input type="text" name="phone" placeholder="Enter your phone number" value="{{ request.form.get('phone', '') }}">

        <label for="date">Date: <span style="color:red">*</span></label>
        <input type="date" name="date" required value="{{ request.form.get('date', '') or current_date }}">

        <label for="letter_type">Letter Type: <span style="color:red">*</span></label>
        <select name="letter_type" id="letter_type" required onchange="updateForm()">
            <option value="">-- Select Letter Type --</option>
            <option value="school_leave" {% if request.form.get('letter_type') == 'school_leave' %}selected{% endif %}>School Leave</option>
            <option value="office_leave" {% if request.form.get('letter_type') == 'office_leave' %}selected{% endif %}>Office Leave</option>
            <option value="bank_application" {% if request.form.get('letter_type') == 'bank_application' %}selected{% endif %}>Bank Application</option>
            <option value="fee_concession" {% if request.form.get('letter_type') == 'fee_concession' %}selected{% endif %}>Fee Concession</option>
            <option value="character_certificate" {% if request.form.get('letter_type') == 'character_certificate' %}selected{% endif %}>Character Certificate</option>
            <option value="custom" {% if request.form.get('letter_type') == 'custom' %}selected{% endif %}>Custom</option>
        </select>

        <div id="recipient_div" class="hidden">
            <label for="recipient">Recipient Name/Title:</label>
            <input type="text" name="recipient" id="recipient" placeholder="Recipient Name/Title" value="{{ request.form.get('recipient', '') }}">
        </div>

        <div id="org_name_div" class="hidden">
            <label for="org_name" id="org_name_label">School/Office/Organization Name:</label>
            <input type="text" name="org_name" id="org_name" placeholder="Enter organization name" value="{{ request.form.get('org_name', '') }}">
        </div>

        <div id="address_div" class="hidden">
            <label for="address" id="address_label">Recipient Address:</label>
            <textarea name="address" id="address" placeholder="Enter recipient's address" rows="3">{{ request.form.get('address', '') }}</textarea>
        </div>

        <div id="job_title_div" class="hidden">
            <label for="job_title">Your Job Title (optional):</label>
            <input type="text" name="job_title" id="job_title" placeholder="Enter your job title" value="{{ request.form.get('job_title', '') }}">
        </div>

        <label for="reason">Reason / Details: <span style="color:red">*</span></label>
        <textarea name="reason" placeholder="Enter reason or details" rows="4" required>{{ request.form.get('reason', '') }}</textarea>

        <div id="dates_div" class="hidden">
            <label for="from_date">From Date (if applicable):</label>
            <input type="date" name="from_date" value="{{ request.form.get('from_date', '') }}">

            <label for="to_date">To Date (if applicable):</label>
            <input type="date" name="to_date" value="{{ request.form.get('to_date', '') }}">
        </div>

        <button type="submit">Generate Letter</button>
    </form>

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    {% if letter %}
    <h2>Generated Letter:</h2>
    <div class="letter-box">{{ letter | safe }}</div>
    {% endif %}

<script>
function updateForm() {
    const type = document.getElementById('letter_type').value;

    const recipientDiv = document.getElementById('recipient_div');
    const orgNameDiv = document.getElementById('org_name_div');
    const addressDiv = document.getElementById('address_div');
    const jobTitleDiv = document.getElementById('job_title_div');
    const datesDiv = document.getElementById('dates_div');

    const recipientInput = document.getElementById('recipient');
    const orgNameInput = document.getElementById('org_name');
    const addressLabel = document.getElementById('address_label');
    const addressInput = document.getElementById('address');

    // Hide all dynamic fields by default
    recipientDiv.classList.add('hidden');
    orgNameDiv.classList.add('hidden');
    addressDiv.classList.add('hidden');
    jobTitleDiv.classList.add('hidden');
    datesDiv.classList.add('hidden');

    if(type === 'school_leave') {
        recipientDiv.classList.remove('hidden');
        orgNameDiv.classList.remove('hidden');
        addressDiv.classList.remove('hidden');
        datesDiv.classList.remove('hidden');

        recipientInput.placeholder = "Principal / Teacher's Name";
        orgNameInput.placeholder = "Enter school name";
        addressLabel.innerText = "School Address:";
        addressInput.placeholder = "Enter school's full address";
    }
    else if(type === 'office_leave') {
        recipientDiv.classList.remove('hidden');
        orgNameDiv.classList.remove('hidden');
        addressDiv.classList.remove('hidden');
        jobTitleDiv.classList.remove('hidden');
        datesDiv.classList.remove('hidden');

        recipientInput.placeholder = "Manager / Supervisor Name";
        orgNameInput.placeholder = "Enter office/company name";
        addressLabel.innerText = "Office Address:";
        addressInput.placeholder = "Enter office's full address";
    }
    else if(type === 'bank_application') {
        recipientDiv.classList.remove('hidden');
        orgNameDiv.classList.remove('hidden');
        addressDiv.classList.remove('hidden');

        recipientInput.placeholder = "Branch Manager";
        orgNameInput.placeholder = "Enter bank branch name";
        addressLabel.innerText = "Bank Branch Address:";
        addressInput.placeholder = "Enter bank branch's address";
    }
    else if(type === 'fee_concession' || type === 'character_certificate') {
        recipientDiv.classList.remove('hidden');

        recipientInput.placeholder = "Principal / Authority Name";
    }
    else {
        // Custom or others: minimal fields
        recipientDiv.classList.remove('hidden');
        orgNameDiv.classList.remove('hidden');
        addressDiv.classList.remove('hidden');

        recipientInput.placeholder = "Recipient Name/Title";
        orgNameInput.placeholder = "Enter full organization name";
        addressLabel.innerText = "Address:";
        addressInput.placeholder = "Enter full address";
    }
}
// Run on page load to set correct fields
window.onload = updateForm;
</script>

</body>
</html>
"""

def generate_letter_with_ai(name, your_address, email, phone, date, letter_type, recipient, org_name, address, job_title, reason, from_date, to_date):
    # Build letter info only if fields are provided (no empty placeholders)
    info = []
    info.append(f"Sender's name: {name}")
    info.append(f"Sender's full address: {your_address}")
    if email:
        info.append(f"Sender's email: {email}")
    if phone:
        info.append(f"Sender's phone number: {phone}")
    info.append(f"Date: {date}")
    if recipient:
        info.append(f"Recipient name/title: {recipient}")
    if org_name:
        info.append(f"Recipient organization name: {org_name}")
    if address:
        info.append(f"Recipient address: {address}")
    if job_title:
        info.append(f"Sender's job title: {job_title}")

    info.append(f"Reason/details: {reason}")
    if from_date and to_date:
        info.append(f"The leave dates are from {from_date} to {to_date}.")

    prompt = (
        "You are a helpful assistant who writes polite, formal letters.\n\n"
        + "\n".join(info) +
        "\n\nPlease write the full letter including the sender's address, date, greeting, body, closing, signature, and contact details if provided. "
        "Do NOT include any placeholders like [Your Address]. Use the data provided fully and omit any info not given."
    )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant who writes polite formal letters."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        ai_text = data["choices"][0]["message"]["content"]
        return ai_text.strip()
    except Exception as e:
        return f"Error generating letter: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def home():
    letter = None
    error = None
    current_date = datetime.now().strftime("%Y-%m-%d")
    if request.method == "POST":
        name = request.form.get("name")
        your_address = request.form.get("your_address")
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        date = request.form.get("date") or current_date
        letter_type = request.form.get("letter_type")
        recipient = request.form.get("recipient", "").strip()
        org_name = request.form.get("org_name", "").strip()
        address = request.form.get("address", "").strip()
        job_title = request.form.get("job_title", "").strip()
        reason = request.form.get("reason")
        from_date = request.form.get("from_date", "")
        to_date = request.form.get("to_date", "")

        if not all([name, your_address, date, letter_type, reason]):
            error = "Please fill in all required fields: Your Name, Your Address, Date, Letter Type, and Reason."
        else:
            letter = generate_letter_with_ai(name, your_address, email, phone, date, letter_type, recipient, org_name, address, job_title, reason, from_date, to_date)
            if letter.startswith("Error"):
                error = letter
                letter = None

    return render_template_string(HTML, letter=letter, error=error, request=request, current_date=current_date)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
