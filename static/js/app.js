const API = "http://127.0.0.1:5000"
function signup(){
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const phno = document.getElementById("phno").value.trim();
    const collegename = document.getElementById("collegename").value.trim();
    if (!username || !email || !password || !phno || !collegename) {
        alert("Please fill in all fields.");
        return;
    }
    fetch(API  + "/register", {
        method: "POST",
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
             username: username,
             email: email,
             password: password,
             phno: phno,
             collegename: collegename
         })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        if (data.token) {
            localStorage.setItem("token", data.token);
            alert("Signup successful!");
            window.location = "/dashboard";
        } else {
            alert(data.error || "Signup failed." );
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while signing up.");
    });
}

function login(){
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    if (!email || !password) {
        alert("Please fill all fields.");
        return;
    }
    fetch(API + "/login", {
        method: "POST",
        headers:{
            "Content-Type": "application/json"
    },
        body: JSON.stringify({ email:email,
             password:password
             })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        if (data.token) {
            localStorage.setItem("token", data.token);
            alert("Login successful!");
            window.location = "/dashboard";
        } else {
            alert(data.error || "Login failed.");
        }
    })
    .catch(error => {
        console.log("Error:", error);
        alert("server error");
    });
}
function createNote() {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Please Login First");
        window.location = "/";
        return;
    }
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    if (!title || !description) {
        alert("Please enter Title and Description");
        return;
    }
    fetch(API + "/create_note", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": token
        },
        body: JSON.stringify({
            title: title,
            description: description
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        document.getElementById("title").value = "";
        document.getElementById("description").value = "";
        getNotes();
    })
    .catch(err => {
        console.log(err);
    });
}

function getNotes() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location = "/";
        return;
    }
    fetch(API + "/get_note", {
        method: "GET",
        headers: {
            "Authorization": token
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            localStorage.removeItem("token");
            window.location = "/";
            return;
        }
        let html = "";
        if (data.notes.length === 0) {
            html = `
            <div class="empty-notes">
                <h3> No Notes Found</h3>
                <p>Create your first note.</p>
            </div>
            `;
        } else {
            data.notes.forEach(note => {
                html += `
                <div class="note">
                    <h3>${note.title}</h3>
                    <p>${note.description}</p>
                    <small>${note.created_at}</small>
                    <div class="note-buttons">
                        <button class="edit-btn"
                        onclick="editNote(${note.note_id},
                        '${note.title}',
                        '${note.description}')">
                        ✏ Edit
                        </button>
                        <button class="delete-btn"
                        onclick="deleteNote(${note.note_id})">
                        Delete
                        </button>
                    </div>
                </div>
                `;
            });
        }
        document.getElementById("notes").innerHTML = html;
    })
    .catch(err => {
        console.log(err);
    });
}

function editNote(id, title, description) {
    const token = localStorage.getItem("token");
    let newTitle = prompt("Title", title);
    let newDescription = prompt("Description", description);
    if (newTitle == null || newDescription == null)
        return;
    fetch(API + "/update_note/" + id, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": token
        },
        body: JSON.stringify({
            title: newTitle,
            description: newDescription
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        getNotes();
    });
}


function deleteNote(id) {
    const token = localStorage.getItem("token");
    if (!confirm("Delete this note?"))
        return;
    fetch(API + "/delete_note/" + id, {
        method: "DELETE",
        headers: {
            "Authorization": token
        }
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        getNotes();
    });
}

function logout() {
    localStorage.removeItem("token");
    alert("Logged Out");
    window.location = "/";
}

if (window.location.pathname === "/dashboard") {
    getNotes();
}