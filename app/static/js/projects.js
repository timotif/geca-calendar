document.getElementById('loader').style.display = 'none';
document.addEventListener('DOMContentLoaded', async () => {
const btn = document.getElementsByClassName('submit-list').disabled = true;
document.getElementById('loader').style.display = 'block';
// Fetch projects
const response = await fetch('/fetch_projects');
const data = await response.json();
const projectsList = document.getElementById('projects-list');

for (const p of data) {
	li = document.createElement('li');
	li.className = "list-group-item d-flex justify-content-between align-items-center";

	checkbox = document.createElement('input');
	checkbox.type = 'checkbox';
	checkbox.name = 'selected_projects';
	checkbox.value = p.id;
	checkbox.className = 'form-check-input me-2';
	
	li.appendChild(checkbox);
	li.appendChild(document.createTextNode(p.name));
	projectsList.appendChild(li);
}
const projects = document.getElementById('projects-form');
projects.appendChild(projectsList);
document.getElementById('loader').style.display = 'none';
document.getElementById('projects').style.display = 'block';
btn.disabled = false;
})