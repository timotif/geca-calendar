document.addEventListener('DOMContentLoaded', async () => {
	const btn = document.getElementsByClassName('submit-list').disabled = true;
	document.getElementById('loader').style.display = 'block';

	// Fetch projects
	const response = await fetch('/fetch_projects');
	const data = await response.json();
	const projectGrid = document.getElementById('projects-grid');

	for (const p of data) {
		const col = document.createElement('div');
		col.className = 'col-md-6 mb-3';
		
		const card = document.createElement('div');
		card.className = 'card project-card';
		card.dataset.id = p.id;

		// Create hidden input to store selected projects
		const hiddenInput = document.createElement('input');
		hiddenInput.type = 'hidden';
		hiddenInput.name = 'selected_projects';
		hiddenInput.value = p.id;
		hiddenInput.disabled = true;
		
		card.appendChild(hiddenInput);
		card.appendChild(document.createTextNode(p.name));

		// Add event listener to each project
		card.addEventListener('click', () => {
			card.classList.toggle('selected');
			hiddenInput.disabled = !hiddenInput.disabled;
		});
		col.appendChild(card);
		projectGrid.appendChild(col);
	}
	document.getElementById('loader').style.display = 'none';
	document.getElementById('projects').style.display = 'block';
	btn.disabled = false;
})