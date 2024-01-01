import streamlit as st
import requests
import json
import os


def buddy_letter_generator(form_data, api_key):
  api_key = os.environ.get('openai_api_key')
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {api_key}'
  }

  # Prepare the messages for the API request
  system_message = {
      "role":
      "system",
      "content":
      "You are a helpful assistant skilled in writing Buddy Letters for Veterans Affairs disability claims."
  }
  user_message = {
      "role":
      "user",
      "content":
      f"Write a Buddy Letter based on this information:\n{json.dumps(form_data, indent=2)}. Try to match the writing style of the information provided, if possible.  If not, then try to write in a simple, succinct and consise manner."
  }

  data = {
      "model": "gpt-4-1106-preview",
      "messages": [system_message, user_message]
  }

  try:
    response = requests.post('https://api.openai.com/v1/chat/completions',
                             headers=headers,
                             json=data)

    if response.status_code == 200:
      generated_content = response.json().get('choices', [{}])[0].get(
          'message', {}).get('content', 'No content generated')
      # Append the certification statement before returning the content
      return generated_content + "\n\nI CERTIFY THAT I have completed this statement and that its information is true and correct to the best of my knowledge and belief."
    else:
      st.error(f"OpenAI API Error: {response.status_code} - {response.text}")
      return None
  except requests.exceptions.RequestException as e:
    st.error(f"Request failed: {e}")
    return None
  except json.JSONDecodeError:
    st.error("Failed to parse response from OpenAI API.")
    return None
  except KeyError:
    st.error("Unexpected response format from OpenAI API.")
    return None
  except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
    return None


# Streamlit Form for Buddy Letter Generator
with st.form(key="buddy_letter_form"):
  st.title('Buddy Letter Generator for VA Claims')

  # Display writing tips and guidelines
  st.markdown("## Instructions")
  st.markdown(
      "Please fill out the form below with the details for the Buddy Letter. Remember to keep it brief and to the point, and avoid diagnoses unless you are a licensed provider."
  )
  st.markdown("## Tips")
  st.markdown(
      "The purpose of a buddy letter is to (A) help prove a service connection, (B) help prove severity of a disability, or (C) both. This form has fields for both, but feel free to ignore fields that don't apply."
  )
  st.warning("## ⚠️ Privacy Notice")
  st.markdown(
      "Be aware that information submitted here will be processed by OpenAI and is subject to their [privacy policy](https://openai.com/privacy/)."
  )
  st.warning("### ⚠️ Important Notes: ")
  st.markdown(
      "This application is NOT intended for submission of personal health information (PHI) or Personal Identifiable Information (PII). Use dummy information where needed."
  )
  st.markdown("### NOTE: ")
  st.markdown(
      "If you encounter an error, it may be due to high demand on the OpenAI API. Please try again after a short wait."
  )

  # Form fields
  name = st.text_input('Your Name*',
                       placeholder="Enter your full name",
                       value="")
  veteran_name = st.text_input('Veteran Name*',
                               placeholder="Enter the veteran's full name",
                               value="")
  relationship_to_veteran = st.text_input(
      'Your Relationship to the Veteran*',
      placeholder="E.g., Fellow service member, family member",
      value="")
  knowledge_of_veteran = st.text_area(
      'How You Know the Veteran',
      placeholder="Describe how and for how long you've known the veteran",
      value="")
  event_details = st.text_area(
      'If you are trying to prove service connection, then list the details of the witnessed event or change',
      placeholder=
      "Describe the event you witnessed.  If applicable, describe how the veteran changed as a result of this event.",
      value="")
  # Form fields for Observations and Impact on Daily Life
  condition_observations = st.text_area(
      'Observations of the Veteran’s Condition',
      placeholder=
      "Be sure to include frequency, duration, and severity of symptoms",
      value="")
  impact_on_daily_life = st.text_area(
      'Impact on Daily Life',
      placeholder=
      "Describe the effect of the condition on the veteran's daily activities, work, and personal life",
      value="")
  additional_comments = st.text_area(
      'Additional Comments',
      placeholder="Add any other relevant comments or information",
      value="")

  # Certification Statement Reminder
  #    st.markdown("### Certification Statement Reminder")
  #    st.markdown("If you're not using the VA form, remember to include the certification statement: *'I CERTIFY THAT I have completed this statement and that its information is true and correct to the best of my knowledge and belief.'*")

  # Submit button
  submit_button = st.form_submit_button('Generate Buddy Letter')

  if submit_button:
    # Check for empty required fields
    required_fields_filled = all(
        [name, relationship_to_veteran, knowledge_of_veteran])

    # Initialize a flag to track validation
    all_fields_valid = True

    if required_fields_filled:
      # Validate required fields
      if not name:
        st.warning('Please enter your name.')
        all_fields_valid = False
      if not relationship_to_veteran:
        st.warning('Please enter your relationship to the veteran.')
        all_fields_valid = False
      if not knowledge_of_veteran:
        st.warning('Please describe how you know the veteran.')
        all_fields_valid = False

    if all_fields_valid:
      # Aggregate form data
      # Update the form data aggregation with new fields
      form_data = {
          'name': name,
          'veteran_name': veteran_name,
          'relationship_to_veteran': relationship_to_veteran,
          'knowledge_of_veteran': knowledge_of_veteran,
          'event_details': event_details,
          'condition_observations': condition_observations,
          'impact_on_daily_life': impact_on_daily_life,
          'additional_comments': additional_comments
      }
      # Retrieve the API key from the environment variable
      api_key = os.environ.get('openai_api_key')

      # Show loading spinner and generate the letter
      with st.spinner('Generating your Buddy Letter, please wait...'):
        letter = buddy_letter_generator(form_data, api_key)

      # Show confirmation message
      st.success('Your Buddy Letter has been generated!')
      st.markdown(letter)
    else:
      # Display error if required fields are not filled
      st.error('Please fill in all required fields.')
