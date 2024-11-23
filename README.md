# Coffee Shop Management System ☕

Welcome to the **Coffee Shop Management System**, a robust Streamlit web application designed to streamline and enhance coffee shop operations. This app includes features for customers and administrators, offering an intuitive interface to manage orders, inventory, promotions, analytics, and more.

## 🚀 Live Demo
The application has been deployed using Streamlit Cloud. You can access it here:  
[Coffee Shop Management System](https://appcoffeeapp-7bmxg7hufgmtyg2iwwfycr.streamlit.app/)

---

## 📋 Features
### **Customer Features**
- **Order Coffee**: Browse the menu, select your favorite coffee, and place an order.
- **Order History**: View a list of your past orders with details.
- **Pickup Notifications**: Get real-time updates on your order status.
- **Feedback**: Share your experience to help us improve.

### **Admin Features**
- **Inventory Management**: Track and update coffee shop inventory.
- **Sales Reporting**: Access detailed sales reports and performance metrics.
- **Analytics Dashboard**: Gain insights into customer trends and behavior.
- **Promotions & Discounts**: Manage promotional campaigns and coupon codes.
- **Notifications**: Send updates and alerts to customers.
- **About Us**: Learn more about the **Espresso Dev Team** behind this application.

---

## 🛠️ Technologies Used
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: [Firebase Firestore](https://firebase.google.com/products/firestore)
- **Payment Gateway**: [Stripe](https://stripe.com/)
- **Data Visualization**: [Plotly](https://plotly.com/)
- **Image Processing**: [Pillow](https://pillow.readthedocs.io/)

---

## ⚙️ Installation
To set up the application locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/HengYpinn/streamlit_CoffeeApp.git
   cd streamlit_CoffeeApp
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate     # For Windows
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
4. Add your Firebase and Stripe credentials to .streamlit/secrets.toml:
   ```bash
   [firebase]
   type = "service_account"
   project_id = "your_project_id"
   private_key_id = "your_private_key_id"
   private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
   client_email = "your_client_email"
   client_id = "your_client_id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your_client_x509_cert_url"
  
   [stripe]
   api_key = "your_stripe_secret_key"
5. Run the application:
   ```bash
   streamlit run main.py
## 📂 Project Structure

```plaintext
streamlit_CoffeeApp/
├── analytics/               # Analytics dashboard logic
├── auth/                    # Authentication module
├── feedback/                # Feedback submission functionality
├── firebase_init/           # Firebase initialization
├── inventory/               # Inventory management logic
├── main.py                  # Main entry point of the app
├── menu/                    # Menu items and pricing
├── notification/            # Notification management
├── order/                   # Customer order logic
├── order_history/           # Order history display
├── pickup_notification/     # Pickup notification feature
├── promotions/              # Promotions and discount management
├── sales_reporting/         # Sales reporting logic
├── utils/                   # Utility functions
├── requirements.txt         # Dependencies
└── .streamlit/secrets.toml  # Secrets file (not for public repositories)```
```
## 📝 License

This project is licensed under the [MIT License](https://mit-license.org/).
