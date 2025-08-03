import streamlit as st

def main():
    st.title("My Streamlit App")
    st.write("Welcome to my first Streamlit application!")
    
    # Add more Streamlit components here
    user_input = st.text_input("Enter some text:")
    if st.button("Submit"):
        st.write(f"You entered: {user_input}")

if __name__ == "__main__":
    main()