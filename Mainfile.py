import streamlit as st
import pickle
import os
import random

# File path for saving all data
SAVE_FILE = "f1_simulation_data.pkl"

# Initialize session state to store the data
def init_data():
    if 'data' not in st.session_state:
        st.session_state['data'] = {
            'teams': [],
            'drivers': [],
            'hall_of_fame': [],
            'former_teams': [],
            'former_drivers': [],
            'team_champions': []
        }

init_data()

# Save progress to a single file
def save_progress():
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(st.session_state['data'], f)
    st.success("Progress saved to device!")

# Load progress from a single file
def load_progress():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'rb') as f:
            st.session_state['data'] = pickle.load(f)
        st.success("Progress loaded!")
    else:
        st.warning("No save file found!")

# Save progress locally for download
def save_to_device():
    data = pickle.dumps(st.session_state['data'])
    st.download_button(
        label="Download Save File",
        data=data,
        file_name="f1_simulation_data.pkl",
        mime="application/octet-stream"
    )

# Load progress from a local file
def load_from_device(file):
    if file is not None:
        st.session_state['data'] = pickle.loads(file.read())
        st.success("Progress loaded from file!")

# Add driver to hall of fame
def add_to_hall_of_fame(driver_name):
    for driver in st.session_state['data']['drivers']:
        if driver['name'] == driver_name:
            driver['retired'] = True
            st.session_state['data']['drivers'].remove(driver)
            st.session_state['data']['hall_of_fame'].append({
                'name': driver['name'],
                'nationality': driver['nationality'],
                'age': driver['age'],
                'wdcs': driver['wdcs'],
                'constructor_championships': driver['constructor_championships'],
                'stats': driver['stats']
            })
            st.success(f"Driver {driver_name} added to Hall of Fame!")
            break

# Hall of Fame page
def view_hall_of_fame():
    if len(st.session_state['data']['hall_of_fame']) > 0:
        st.write("### Hall of Fame")
        for member in st.session_state['data']['hall_of_fame']:
            st.write(f"**Name**: {member['name']}")
            st.write(f"**Nationality**: {member['nationality']}")
            st.write(f"**Age**: {member['age']}")
            st.write(f"**WDCs**: {member['wdcs']}")
            st.write(f"**Constructor Championships**: {member['constructor_championships']}")
            st.write(f"**Stats**: {member['stats']}")
            st.write("---")
    else:
        st.write("Hall of Fame is empty!")

# Add driver functionality
def add_driver():
    driver_name = st.text_input("Enter driver name:")
    nationality = st.text_input("Enter driver's nationality:")
    age = st.number_input("Enter driver's age", min_value=18, max_value=100, value=18)
    racecraft = st.slider("Racecraft", 1, 100)
    overtaking = st.slider("Overtaking", 1, 100)
    iq = st.slider("IQ", 1, 100)
    focus = st.slider("Focus", 1, 100)
    potential = st.slider("Potential", 1, 100)
    
    team_name = st.selectbox("Choose a team", [team['name'] for team in st.session_state['data']['teams'] if not team['bankrupt']])

    if st.button("Add Driver"):
        if driver_name and nationality and team_name:
            overall = (racecraft + overtaking + iq + focus + potential) / 5
            driver = {
                'name': driver_name,
                'nationality': nationality,
                'age': age,
                'stats': {'racecraft': racecraft, 'overtaking': overtaking, 'iq': iq, 'focus': focus, 'potential': potential, 'overall': overall},
                'team': team_name,
                'retired': False,
                'wdcs': 0,
                'constructor_championships': 0
            }
            # Add driver to team
            for team in st.session_state['data']['teams']:
                if team['name'] == team_name:
                    team['drivers'].append(driver)
            st.session_state['data']['drivers'].append(driver)
            st.success(f"Driver {driver_name} added to team {team_name}!")

# Main app
def main():
    menu = [
        "Drivers", "Teams", "Database", "Simulate",
        "Restore Driver", "Restore Team", "Delete Team/Driver",
        "Hall of Fame", "Save/Load Progress"
    ]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Drivers":
        st.write("### Drivers")
        for driver in st.session_state['data']['drivers']:
            st.write(f"**Name**: {driver['name']}")
            st.write(f"**Nationality**: {driver['nationality']}")
            st.write(f"**Age**: {driver['age']}")
            st.write(f"**Team**: {driver['team']}")
            st.write(f"**Overall**: {driver['stats']['overall']:.2f}")
            st.write("---")
        if st.button("Add Driver"):
            add_driver()

    elif choice == "Teams":
        st.write("### Teams")
        for team in st.session_state['data']['teams']:
            st.write(f"**Name**: {team['name']}")
            st.write(f"**Nationality**: {team['nationality']}")
            st.write(f"**Drivers**: {[d['name'] for d in team['drivers']]}")
            st.write("---")
        if st.button("Add Team"):
            team_name = st.text_input("Enter team name:")
            nationality = st.text_input("Enter team nationality:")
            if st.button("Confirm Add Team"):
                st.session_state['data']['teams'].append({
                    'name': team_name,
                    'nationality': nationality,
                    'drivers': []
                })
                st.success(f"Team {team_name} added!")

    elif choice == "Database":
        st.write("### Driver Database")
        avg_overall = sum([driver['stats']['overall'] for driver in st.session_state['data']['drivers']]) / len(st.session_state['data']['drivers'])
        st.write(f"Average Overall Rating: {avg_overall:.2f}")

    elif choice == "Simulate":
        st.write("### Simulate Season")
        # Simulation logic
        if st.button("Simulate Another Year"):
            st.success("Simulated another year!")

    elif choice == "Restore Driver":
        st.write("### Restore Driver")
        # Restore driver logic

    elif choice == "Restore Team":
        st.write("### Restore Team")
        # Restore team logic

    elif choice == "Delete Team/Driver":
        st.write("### Delete Team or Driver")
        # Delete logic

    elif choice == "Hall of Fame":
        view_hall_of_fame()

    elif choice == "Save/Load Progress":
        if st.button("Save Progress"):
            save_progress()
        if st.button("Load Progress"):
            load_progress()
        save_to_device()

if __name__ == '__main__':
    main()
