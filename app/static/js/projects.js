document.addEventListener('DOMContentLoaded', async () => {
	const btn = document.getElementsByClassName('submit-list').disabled = true;
	document.getElementById('loader').style.display = 'block';

	// Fetch projects
	const response = await fetch('/fetch_projects');
	const data = await response.json();
	const projectsList = document.getElementById('projects-list');

	for (const p of data) {
		const li = document.createElement('li');
		li.className = "list-group-item d-flex justify-content-between align-items-center";
		li.dataset.id = p.id;

		// Create hidden input to store selected projects
		const hiddenInput = document.createElement('input');
		hiddenInput.type = 'hidden';
		hiddenInput.name = 'selected_projects';
		hiddenInput.value = p.id;
		hiddenInput.disabled = true;
		
		li.appendChild(hiddenInput);
		li.appendChild(document.createTextNode(p.name));

		// Add event listener to each project
		li.addEventListener('click', () => {
			li.classList.toggle('selected');
			hiddenInput.disabled = !hiddenInput.disabled;
		});
		projectsList.appendChild(li);
	}
	const projects = document.getElementById('projects-form');
	projects.appendChild(projectsList);
	document.getElementById('loader').style.display = 'none';
	document.getElementById('projects').style.display = 'block';
	btn.disabled = false;
})