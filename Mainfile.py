import streamlit as st
import pickle
import os
import random
import uuid  # Import uuid to generate unique IDs for teams

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
            'wdc_history': [],
            'retired_drivers': []  # New list to store retired drivers
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
    option = st.radio("Select an option:", ["View Drivers", "Add Driver", "Edit Driver", "Retire Driver", "Transfer Driver", "Add to Hall of Fame", "Restore Driver"])

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

    elif option == "Edit Driver":
        driver_name = st.selectbox("Select a driver to edit", [driver['name'] for driver in st.session_state['data']['drivers']])

        if driver_name:
            driver = next(driver for driver in st.session_state['data']['drivers'] if driver['name'] == driver_name)

            # Edit fields for selected driver
            driver_name = st.text_input("Edit driver name", value=driver['name'])
            nationality = st.text_input("Edit nationality", value=driver['nationality'])
            age = st.number_input("Edit age", min_value=18, max_value=100, value=driver['age'])
            racecraft = st.slider("Edit Racecraft", 1, 100, value=driver['stats']['racecraft'])
            overtaking = st.slider("Edit Overtaking", 1, 100, value=driver['stats']['overtaking'])
            iq = st.slider("Edit IQ", 1, 100, value=driver['stats']['iq'])
            focus = st.slider("Edit Focus", 1, 100, value=driver['stats']['focus'])
            potential = st.slider("Edit Potential", 1, 100, value=driver['stats']['potential'])

            if st.button("Save Edits"):
                # Update the driver's attributes
                driver['name'] = driver_name
                driver['nationality'] = nationality
                driver['age'] = age
                driver['stats'] = {'racecraft': racecraft, 'overtaking': overtaking, 'iq': iq, 'focus': focus, 'potential': potential}
                driver['stats']['overall'] = (racecraft + overtaking + iq + focus + potential) / 5  # Recalculate overall stat

                st.success(f"Driver {driver_name} has been updated!")

    elif option == "Transfer Driver":
        driver_name = st.selectbox("Select a driver to transfer", [driver['name'] for driver in st.session_state['data']['drivers']])

        if driver_name:
            driver = next(driver for driver in st.session_state['data']['drivers'] if driver['name'] == driver_name)

            # Choose a new team to transfer to
            new_team = st.selectbox("Select a new team", [team['name'] for team in st.session_state['data']['teams'] if not team['bankrupt']])

            if st.button("Transfer Driver"):
                # Remove driver from old team
                old_team = next(team for team in st.session_state['data']['teams'] if team['name'] == driver['team'])
                old_team['drivers'] = [d for d in old_team['drivers'] if d['name'] != driver_name]

                # Add driver to new team
                driver['team'] = new_team
                for team in st.session_state['data']['teams']:
                    if team['name'] == new_team:
                        team['drivers'].append(driver)

                st.success(f"Driver {driver_name} has been transferred to {new_team}!")

    elif option == "Retire Driver":
        driver_name = st.selectbox("Select a driver to retire", [driver['name'] for driver in st.session_state['data']['drivers'] if not driver['retired']])

        if st.button("Retire Driver"):
            for driver in st.session_state['data']['drivers']:
                if driver['name'] == driver_name:
                    driver['retired'] = True  # Mark the driver as retired
                    driver['retirement_reason'] = "Retired"  # Optional, you can add a reason for retirement
                    st.session_state['data']['retired_drivers'].append(driver)  # Add the retired driver to the retired list
                    st.session_state['data']['drivers'] = [d for d in st.session_state['data']['drivers'] if d['name'] != driver_name]  # Remove from active drivers
                    st.success(f"Driver {driver_name} has been retired!")
                    break  # Exit the loop once the driver is found and retired

    elif option == "Restore Driver":
        driver_name = st.selectbox("Select a driver to restore", [driver['name'] for driver in st.session_state['data']['retired_drivers']])

        if st.button("Restore Driver"):
            for driver in st.session_state['data']['retired_drivers']:
                if driver['name'] == driver_name:
                    driver['retired'] = False  # Set the driver's retired status back to False
                    st.session_state['data']['drivers'].append(driver)  # Restore the driver back to active drivers
                    st.session_state['data']['retired_drivers'] = [d for d in st.session_state['data']['retired_drivers'] if d['name'] != driver_name]  # Remove from retired list
                    st.success(f"Driver {driver_name} has been restored!")
                    break  # Exit the loop once the driver is found and restored

    elif option == "Add to Hall of Fame":
        driver_name = st.selectbox("Select driver to add to Hall of Fame", [driver['name'] for driver in st.session_state['data']['drivers']])
        if st.button("Add to Hall of Fame"):
            for driver in st.session_state['data']['drivers']:
                if driver['name'] == driver_name:
                    st.session_state['data']['hall_of_fame'].append(driver)
                    st.success(f"Driver {driver_name} added to Hall of Fame!")

# Teams Page and other pages (not changed)
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
            if team_name:
                team_id = str(uuid.uuid4())  # Generate a unique ID for the team
                st.session_state['data']['teams'].append({
                    'id': team_id,  # Assign the unique ID
                    'name': team_name,
                    'nationality': nationality,
                    'drivers': [],
                    'bankrupt': False,
                    'championships': 0
                })
                st.success(f"Team {team_name} added!")

    elif option == "Retire Team":
        team_name = st.selectbox("Select team to retire", [team['name'] for team in st.session_state['data']['teams']])
        if st.button("Retire Team"):
            for team in st.session_state['data']['teams']:
                if team['name'] == team_name:
                    team['bankrupt'] = True  # Mark the specific team as bankrupt
                    st.session_state['data']['former_teams'].append(team)  # Add to former teams
                    st.session_state['data']['teams'] = [t for t in st.session_state['data']['teams'] if t['name'] != team_name]  # Remove retired team
                    st.success(f"Team {team_name} has been retired!")
                    break  # Exit the loop once the team is found and retired

    elif option == "Restore Team":
        team_name = st.selectbox("Select bankrupt team to restore", [team['name'] for team in st.session_state['data']['former_teams']])
        if st.button("Restore Team"):
            for team in st.session_state['data']['former_teams']:
                if team['name'] == team_name:
                    st.session_state['data']['teams'].append(team)
                    st.session_state['data']['former_teams'] = [t for t in st.session_state['data']['former_teams'] if t['name'] != team_name]
                    st.success(f"Team {team_name} has been restored!")

# Simulate Page
def simulate_page():
    st.header("Simulate")
    if st.button("Simulate Season"):
        active_drivers = [d for d in st.session_state['data']['drivers'] if not d['retired']]  # Only consider active drivers
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
