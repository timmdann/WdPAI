// requests_async.js
function clearInput() {
    document.getElementById("getFirstName").value = '';
    document.getElementById("getLastName").value = '';
    document.getElementById("role").selectedIndex = 0;
    document.getElementById("privacyCheck").checked = false;

}

async function sendGetRequest() {
    const url = "http://localhost:8000/team";

    try {
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            updateTeamList(data.team_members);
        } else {
            console.error('Error while retrieving data:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function sendPostRequest() {
    const firstNameElem = document.getElementById("getFirstName");
    const lastNameElem = document.getElementById("getLastName");
    const roleElem = document.getElementById("role");
    const privacyCheck = document.getElementById("privacyCheck");

    if (!firstNameElem || !lastNameElem || !roleElem || !privacyCheck) {
        console.error("All fields must be filled in.");
        return;
    }

    if (!privacyCheck.checked) {
        alert("Please agree to the privacy policy.");
        return;
    }

    const firstName = firstNameElem.value;
    const lastName = lastNameElem.value;
    const role = roleElem.value;

    const data = {
        first_name: firstName,
        last_name: lastName,
        role: role
    };

    try {
        const response = await fetch("http://localhost:8000/team", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            await sendGetRequest();
            clearInput();
        } else if (response.status == 409) {
            showModal();
        } else {
            console.error('Error while adding a team member:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}



function updateTeamList(teamMembers) {
    const teamList = document.getElementById("teamList");

    if (!teamList) {
        console.error("The element for the command list is not present in the DOM.");
        return;
    }
    teamList.innerHTML = '';
    teamMembers.forEach(member => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `${member.first_name} ${member.last_name}<br>${member.role}`;

        const trashIcon = document.createElement("span");
        trashIcon.classList.add("delete-icon");
        trashIcon.innerHTML = '🗑️';

        trashIcon.onclick = async function () {
            try {
                const response = await fetch(`http://localhost:8000/team/${member.id}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                if (response.ok) {
                    await sendGetRequest();
                } else {
                    console.error('Error when deleting a team member:', response.statusText);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        };

        listItem.appendChild(trashIcon);
        teamList.appendChild(listItem);
    });
}


window.onload = function() {
    sendGetRequest();
};

