import streamlit as st
import pandas as pd

def about_us():
    st.title("About Us")
    st.write(
        """
        This application is brewed with passion by the **Espresso Dev Team**.
        Our mission is to provide a seamless coffee shop management experience for administrators and a delightful ordering journey for customers.
        """
    )
    st.subheader("Meet the Team")
    st.write(
        """
        Below are the individuals behind this project:
        """
    )

    # Data for the team members
    team_data = [
        {"No.": 1, "Name": "Heng Yong Pinn", "Student's ID": "20001323"},
        {"No.": 2, "Name": "Afif Nur Hakimy Bin Suhaimi", "Student's ID": "20001378"},
        {"No.": 3, "Name": "Muhammad Haziq Fahim Bin Omor", "Student's ID": "21001539"},
        {"No.": 4, "Name": "Mikhal Bin Andrew Azmin", "Student's ID": "20000689"},
        {"No.": 5, "Name": "Muhammad Ihsan Bin Mohamad Hishamuddin", "Student's ID": "20000732"},
    ]

    # Convert to a pandas DataFrame
    team_df = pd.DataFrame(team_data)

    # Display the table without the index
    st.write(team_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

    st.subheader("Our Vision")
    st.write(
        """
        At Espresso Dev Team, we believe that every great coffee shop deserves an equally great management system. 
        Through this application, we aim to simplify operations, enhance customer satisfaction, and foster innovation in the coffee industry.
        """
    )
    st.subheader("Acknowledgments")
    st.write(
        """
        We extend our heartfelt gratitude to our lecturer, classmates, and all who supported us in the development of this project.
        Your guidance and encouragement were instrumental in turning our ideas into reality.
        """
    )
