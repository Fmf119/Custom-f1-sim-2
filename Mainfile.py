import streamlit as st
import pickle
import os
import random

# File path for saving all data
SAVE_FILE = "f1_simulation_data.pkl"

# Initialize session state to store the data
def init_data():
    if "data" not in st.session_state:
        st.session_state["data"] = {
            "teams": [],
            "drivers": [],
            "hall_of_fame": [],
            "former_teams": [],
            "former_drivers": [],
            "team_champions": [],
            "driver_champions": [],
        }

init_data()

# Save progress to a single file
def save_progress():
    with open(SAVE_FILE, "wb") as f:
        pickle.dump(st.session_state["data"], f)
    st.success("Progress saved to device!")

# Load progress from a single file
def load_progress():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as f:
            st.session_state["data"] = pickle.load(f)
        st.success("Progress loaded!")
    else:
        st.warning("No save file found!")

# Save progress locally for download
def save_to_device():
    data = pickle.dumps(st.session_state["data"])
    st.download_button(
        label="Download Save File",
        data=data,
        file_name="f1_simulation_data.pkl",
        mime="application/octet-stream",
    )

# Load progress from a local file
def load_from_device(file):
    if file is not None:
        st.session_state["data"] = pickle.loads(file.read())
        st.success("Progress loaded from file!")

# Drivers page
def drivers_page():
    st.title("Drivers")

    # View Drivers
    if st.checkbox("View Drivers"):
        if len(st.session_state['data']['drivers']) > 0:
            for driver in st.session_state['data']['drivers']:
                st.write(f"**Name**: {driver['name']} | **Team**: {driver['team']} | "
                         f"**Overall**: {driver['stats']['overall']:.2f} | "
                         f"**Age**: {driver['age']} | **Nationality**: {driver['nationality']}")
        else:
            st.write("No drivers available.")

    # Add Drivers
    if st.checkbox("Add Drivers"):
        driver_name = st.text_input("Enter driver name:")
        nationality = st.text_input("Enter driver's nationality:")
        age = st.number_input("Enter driver's age", min_value=18, max_value=100, value=18)
        racecraft = st.slider("Racecraft", 1, 100)
        overtaking = st.slider("Overtaking", 1, 100)
        iq = st.slider("IQ", 1, 100)
        focus = st.slider("Focus", 1, 100)
        potential = st.slider("Potential", 1, 100)

        team_name = st.selectbox(
            "Choose a team",
            [team["name"] for team in st.session_state["data"]["teams"] if not team["bankrupt"]],
        )

        if st.button("Add Driver"):
            if driver_name and nationality and team_name:
                overall = (racecraft + overtaking + iq + focus + potential) / 5
                driver = {
                    "name": driver_name,
                    "nationality": nationality,
                    "age": age,
                    "stats": {
                        "racecraft": racecraft,
                        "overtaking": overtaking,
                        "iq": iq,
                        "focus": focus,
                        "potential": potential,
                        "overall": overall,
                    },
                    "team": team_name,
                    "retired": False,
                    "retirement_reason": None,
                    "wdcs": 0,
                }
                # Add driver to team
                for team in st.session_state["data"]["teams"]:
                    if team["name"] == team_name:
                        team["drivers"].append(driver)
                st.session_state["data"]["drivers"].append(driver)
                st.success(f"Driver {driver_name} added to team {team_name}!")

    # Retire Drivers
    if st.checkbox("Retire Driver"):
        driver_name = st.selectbox(
            "Select a driver to retire",
            [driver["name"] for driver in st.session_state["data"]["drivers"] if not driver["retired"]],
        )
        if st.button("Retire Driver"):
            for driver in st.session_state["data"]["drivers"]:
                if driver["name"] == driver_name:
                    driver["retired"] = True
                    driver["retirement_reason"] = "Manual Retirement"
                    st.session_state["data"]["former_drivers"].append(driver)
                    st.session_state["data"]["drivers"] = [
                        d for d in st.session_state["data"]["drivers"] if d["name"] != driver_name
                    ]
                    st.success(f"Driver {driver_name} retired!")

    # Transfer Drivers
    if st.checkbox("Transfer Drivers"):
        driver_name = st.selectbox(
            "Select a driver to transfer",
            [driver["name"] for driver in st.session_state["data"]["drivers"] if not driver["retired"]],
        )
        new_team = st.selectbox(
            "Select new team",
            [team["name"] for team in st.session_state["data"]["teams"] if not team["bankrupt"]],
        )
        if st.button("Transfer Driver"):
            for driver in st.session_state["data"]["drivers"]:
                if driver["name"] == driver_name:
                    old_team = driver["team"]
                    driver["team"] = new_team
                    # Update teams
                    for team in st.session_state["data"]["teams"]:
                        if team["name"] == old_team:
                            team["drivers"] = [
                                d for d in team["drivers"] if d["name"] != driver_name
                            ]
                        if team["name"] == new_team:
                            team["drivers"].append(driver)
                    st.success(f"Driver {driver_name} transferred to {new_team}!")

    # Add Drivers to Hall of Fame
    if st.checkbox("Add Driver to Hall of Fame"):
        driver_name = st.selectbox(
            "Select a driver for the Hall of Fame",
            [driver["name"] for driver in st.session_state["data"]["drivers"]],
        )
        if st.button("Add to Hall of Fame"):
            for driver in st.session_state["data"]["drivers"]:
                if driver["name"] == driver_name:
                    st.session_state["data"]["hall_of_fame"].append(driver)
                    st.success(f"Driver {driver_name} added to the Hall of Fame!")

# Other pages (Teams, Simulate, etc.) remain the same as provided in the updated code.

# Main application
def main():
    menu = [
        "Drivers",
        "Teams",
        "Database",
        "Simulate",
        "Restore Driver",
        "Restore Team",
        "Delete Team/Driver",
        "Save/Load Progress",
    ]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Drivers":
        drivers_page()
    # Other page functions would go here...

if __name__ == "__main__":
    main()
