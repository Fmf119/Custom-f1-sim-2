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
            'team_champions': [],
            'wdc_history': []
        }

init_data()

# Save progress to a single file
def save_progress():
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(st.session_state['data'], f)
    st.success("Progress saved to device!")

def load_progress():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'rb') as f:
            st.session_state['data'] = pickle.load(f)
        st.success("Progress loaded!")
    else:
        st.warning("No save file found!")

def save_to_device():
    data = pickle.dumps(st.session_state['data'])
    st.download_button(
        label="Download Save File",
        data=data,
        file_name="f1_simulation_data.pkl",
        mime="application/octet-stream"
    )

def load_from_device(file):
    if file is not None:
        st.session_state['data'] = pickle.loads(file.read())
        st.success("Progress loaded from file!")

# Drivers Page
def drivers_page():
    st.header("Drivers")
    option = st.radio("Select an option:", ["View Drivers", "Add Driver", "Edit Driver", "Retire Driver", "Transfer Driver", "Add to Hall of Fame"])

    if option == "View Drivers":
        if st.session_state['data']['drivers']:
            for driver in st.session_state['data']['drivers']:
                st.write(f"Name: {driver['name']}, Age: {driver['age']}, Nationality: {driver['nationality']}, Team: {driver['team']}")
                st.write(f"WDCs: {driver['wdcs']}, Constructor Championships: {driver['constructor_championships']}")
        else:
            st.write("No drivers available.")

    elif option == "Add Driver":
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
            overall = (racecraft + overtaking + iq + focus + potential) / 5
            driver = {
                'name': driver_name,
                'nationality': nationality,
                'age': age,
                'stats': {'racecraft': racecraft, 'overtaking': overtaking, 'iq': iq, 'focus': focus, 'potential': potential, 'overall': overall},
                'team': team_name,
                'retired': False,
                'retirement_reason': None,
                'wdcs': 0,
                'constructor_championships': 0
            }
            for team in st.session_state['data']['teams']:
                if team['name'] == team_name:
                    team['drivers'].append(driver)
            st.session_state['data']['drivers'].append(driver)
            st.success(f"Driver {driver_name} added to team {team_name}!")

    elif option == "Add to Hall of Fame":
        driver_name = st.selectbox("Select driver to add to Hall of Fame", [driver['name'] for driver in st.session_state['data']['drivers']])
        if st.button("Add to Hall of Fame"):
            for driver in st.session_state['data']['drivers']:
                if driver['name'] == driver_name:
                    st.session_state['data']['hall_of_fame'].append(driver)
                    st.success(f"Driver {driver_name} added to Hall of Fame!")

# Teams Page
def teams_page():
    st.header("Teams")
    option = st.radio("Select an option:", ["View Teams", "Add Team", "Retire Team", "Restore Team"])

    if option == "View Teams":
        if st.session_state['data']['teams']:
            for team in st.session_state['data']['teams']:
                st.write(f"Name: {team['name']}, Nationality: {team['nationality']}, Championships: {team['championships']}")
                st.write(f"Bankrupt: {'Yes' if team['bankrupt'] else 'No'}")
                for driver in team['drivers']:
                    st.write(f"- Driver: {driver['name']}")
        else:
            st.write("No teams available.")

    elif option == "Add Team":
        team_name = st.text_input("Enter team name:")
        nationality = st.text_input("Enter team nationality:")
        if st.button("Add Team"):
            st.session_state['data']['teams'].append({'name': team_name, 'nationality': nationality, 'drivers': [], 'bankrupt': False, 'championships': 0})
            st.success(f"Team {team_name} added!")

    elif option == "Retire Team":
        team_name = st.selectbox("Select team to retire", [team['name'] for team in st.session_state['data']['teams'] if not team['bankrupt']])
        if st.button("Retire Team"):
            for team in st.session_state['data']['teams']:
                if team['name'] == team_name:
                    team['bankrupt'] = True
                    st.session_state['data']['former_teams'].append(team)
                    st.session_state['data']['teams'] = [t for t in st.session_state['data']['teams'] if t['name'] != team_name]
                    st.success(f"Team {team_name} retired!")

    elif option == "Restore Team":
        team_name = st.selectbox("Select bankrupt team to restore", [team['name'] for team in st.session_state['data']['former_teams']])
        if st.button("Restore Team"):
            for team in st.session_state['data']['former_teams']:
                if team['name'] == team_name:
                    st.session_state['data']['teams'].append(team)
                    st.session_state['data']['former_teams'] = [t for t in st.session_state['data']['former_teams'] if t['name'] != team_name]
                    st.success(f"Team {team_name} restored!")

# Simulate Page
def simulate_page():
    st.header("Simulate")
    if st.button("Simulate Season"):
        active_drivers = [d for d in st.session_state['data']['drivers'] if not d['retired']]
        if not active_drivers:
            st.error("No active drivers to simulate!")
            return

        winner_driver = random.choice(active_drivers)
        winner_team = random.choice([team for team in st.session_state['data']['teams'] if not team['bankrupt']])

        winner_driver['wdcs'] += 1
        winner_team['championships'] += 1
        st.session_state['data']['team_champions'].append({
            'year': len(st.session_state['data']['team_champions']) + 1,
            'team': winner_team['name'],
            'driver': winner_driver['name']
        })
        st.session_state['data']['wdc_history'].append(winner_driver['name'])
        st.success(f"WDC Winner: {winner_driver['name']}")
        st.success(f"Constructors' Champion: {winner_team['name']}")

    if st.button("Simulate Another Year"):
        simulate_page()

# Hall of Fame
def hall_of_fame_page():
    st.header("Hall of Fame")
    if st.session_state['data']['hall_of_fame']:
        for member in st.session_state['data']['hall_of_fame']:
            st.write(f"Name: {member['name']}, WDCs: {member['wdcs']}, Constructor Championships: {member['constructor_championships']}")
    else:
        st.write("Hall of Fame is empty.")

# Save/Load
def save_load_page():
    st.header("Save/Load Progress")
    if st.button("Save Progress"):
        save_progress()
    if st.button("Load Progress"):
        load_progress()
    st.write("---")
    file = st.file_uploader("Load from Device", type=["pkl"])
    if file:
        load_from_device(file)
    st.write("---")
    save_to_device()

# Main Page
def main():
    menu = ["Drivers", "Teams", "Simulate", "Hall of Fame", "Save/Load Progress"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Drivers":
        drivers_page()
    elif choice == "Teams":
        teams_page()
    elif choice == "Simulate":
        simulate_page()
    elif choice == "Hall of Fame":
        hall_of_fame_page()
    elif choice == "Save/Load Progress":
        save_load_page()

if __name__ == '__main__':
    main()
