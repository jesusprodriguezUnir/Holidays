document.addEventListener('DOMContentLoaded', () => {
    // --- STATE ---
    const state = {
        teams: [],
        employees: [],
        vacations: [],
        currentTeamId: null,
        currentView: 'quadrant',
        dateRange: []
    };

    // --- ELEMENTS ---
    const els = {
        navBtns: document.querySelectorAll('.nav-btn'),
        views: document.querySelectorAll('.view'),
        teamSelect: document.getElementById('team-select'),
        periodSelect: document.getElementById('period-select'),
        refreshBtn: document.getElementById('refresh-btn'),
        calendarGrid: document.getElementById('calendar-grid'),
        toast: document.getElementById('toast'),

        // Modals
        modalRange: document.getElementById('modal-range'),
        modalTeam: document.getElementById('modal-team'),
        modalEmployee: document.getElementById('modal-employee'),
        closeModalBtns: document.querySelectorAll('.close-modal'),

        // Buttons
        addRangeBtn: document.getElementById('add-range-btn'),
        newTeamBtn: document.getElementById('new-team-btn'),
        newEmployeeBtn: document.getElementById('new-employee-btn'),

        // Forms
        formRange: document.getElementById('form-range'),
        formTeam: document.getElementById('form-team'),
        formEmployee: document.getElementById('form-employee'),

        // Tables
        teamsTableBody: document.querySelector('#teams-table tbody'),
        employeesTableBody: document.querySelector('#employees-table tbody'),

        // Form Inputs
        rangeEmployee: document.getElementById('range-employee'),
        empTeam: document.getElementById('emp-team')
    };

    // --- INITIALIZATION ---
    init();

    function init() {
        setupEventListeners();
        loadTeams();
        loadAllEmployees(); // For management view
    }

    function setupEventListeners() {
        // Navigation
        els.navBtns.forEach(btn => {
            btn.addEventListener('click', () => switchView(btn.dataset.view));
        });

        // Quadrant Controls
        els.teamSelect.addEventListener('change', () => {
            state.currentTeamId = els.teamSelect.value;
            loadQuadrantData();
        });
        els.periodSelect.addEventListener('change', loadQuadrantData);
        els.refreshBtn.addEventListener('click', loadQuadrantData);

        // Modals
        els.addRangeBtn.addEventListener('click', openRangeModal);
        els.newTeamBtn.addEventListener('click', () => openModal(els.modalTeam));
        els.newEmployeeBtn.addEventListener('click', () => {
            populateTeamSelect(els.empTeam);
            openModal(els.modalEmployee);
        });

        els.closeModalBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.add('hidden');
            });
        });

        // Forms
        els.formRange.addEventListener('submit', handleRangeSubmit);
        els.formTeam.addEventListener('submit', handleTeamSubmit);
        els.formEmployee.addEventListener('submit', handleEmployeeSubmit);
    }

    function switchView(viewName) {
        state.currentView = viewName;

        // Update Nav
        els.navBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === viewName);
        });

        // Update Views
        els.views.forEach(view => {
            view.classList.toggle('hidden', view.id !== `view-${viewName}`);
            view.classList.toggle('active', view.id === `view-${viewName}`);
        });

        // Refresh data based on view
        if (viewName === 'quadrant') loadQuadrantData();
        if (viewName === 'teams') renderTeamsTable();
        if (viewName === 'employees') loadAllEmployees();
    }

    // --- DATA LOADING ---

    async function loadTeams() {
        try {
            const res = await fetch('/api/teams');
            state.teams = await res.json();

            // Populate Select
            els.teamSelect.innerHTML = '';
            state.teams.forEach(team => {
                const opt = document.createElement('option');
                opt.value = team.id;
                opt.textContent = team.name;
                els.teamSelect.appendChild(opt);
            });

            // Default selection
            if (state.teams.length > 0) {
                const alfa = state.teams.find(t => t.name === 'Alfa');
                state.currentTeamId = alfa ? alfa.id : state.teams[0].id;
                els.teamSelect.value = state.currentTeamId;
                loadQuadrantData();
            }

            renderTeamsTable();

        } catch (err) {
            console.error(err);
        }
    }

    async function loadAllEmployees() {
        try {
            const res = await fetch('/api/employees');
            state.employees = await res.json();
            renderEmployeesTable();
        } catch (err) {
            console.error(err);
        }
    }

    async function loadQuadrantData() {
        if (!state.currentTeamId) return;

        els.calendarGrid.innerHTML = '<div class="loading-spinner">Cargando...</div>';

        // Calculate Dates
        const period = els.periodSelect.value;
        let start, end;

        if (period === 'navidad2025') {
            start = new Date(2025, 11, 22);
            end = new Date(2026, 0, 7);
        } else if (period === 'verano2025') {
            start = new Date(2025, 5, 15);
            end = new Date(2025, 8, 15);
        } else {
            start = new Date(2025, 0, 1);
            end = new Date(2025, 11, 31);
        }

        // Generate Range
        state.dateRange = [];
        let curr = new Date(start);
        while (curr <= end) {
            state.dateRange.push(new Date(curr));
            curr.setDate(curr.getDate() + 1);
        }

        try {
            // Fetch Employees for Team
            const empRes = await fetch(`/api/employees?team_id=${state.currentTeamId}`);
            const teamEmployees = await empRes.json();

            // Fetch Vacations
            const startStr = formatDate(start);
            const endStr = formatDate(end);
            const vacRes = await fetch(`/api/vacations?team_id=${state.currentTeamId}&start_date=${startStr}&end_date=${endStr}`);
            state.vacations = await vacRes.json();

            renderQuadrant(teamEmployees);

        } catch (err) {
            console.error(err);
            els.calendarGrid.innerHTML = '<div class="error">Error cargando datos</div>';
        }
    }

    // --- RENDERING ---

    function renderQuadrant(employees) {
        const totalCols = 2 + state.dateRange.length;
        els.calendarGrid.style.gridTemplateColumns = `200px 150px repeat(${state.dateRange.length}, 40px)`;
        els.calendarGrid.innerHTML = '';

        // Headers
        createCell('Nombre', 'header-cell corner-header');
        createCell('Rol', 'header-cell corner-header');

        state.dateRange.forEach(date => {
            const day = date.getDate();
            const month = date.toLocaleString('es-ES', { month: 'short' });
            const isWeekend = date.getDay() === 0 || date.getDay() === 6;
            const cell = createCell(`${day}<br>${month}`, `header-cell ${isWeekend ? 'weekend' : ''}`);
            if (isWeekend) cell.style.backgroundColor = '#6c8ebf';
        });

        // Rows
        employees.forEach(emp => {
            createCell(emp.name, 'cell row-header');
            createCell(emp.role || '-', 'cell row-header');

            state.dateRange.forEach(date => {
                const dateStr = formatDate(date);
                const isWeekend = date.getDay() === 0 || date.getDay() === 6;
                const isOnVacation = state.vacations.some(v =>
                    v.employee_id === emp.id && v.date.startsWith(dateStr)
                );

                const cell = createCell(isOnVacation ? 'X' : '',
                    `cell day-cell ${isWeekend ? 'weekend' : ''} ${isOnVacation ? 'vacation' : ''}`
                );

                cell.addEventListener('click', () => toggleVacation(emp.id, dateStr, cell));
            });
        });
    }

    function renderTeamsTable() {
        els.teamsTableBody.innerHTML = '';
        state.teams.forEach(team => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${team.name}</td>
                <td>${team.description || ''}</td>
                <td>
                    <button class="btn-danger" onclick="deleteTeam(${team.id})">Eliminar</button>
                </td>
            `;
            els.teamsTableBody.appendChild(tr);
        });
    }

    function renderEmployeesTable() {
        els.employeesTableBody.innerHTML = '';
        state.employees.forEach(emp => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${emp.name}</td>
                <td>${emp.role || ''}</td>
                <td>${emp.team_name}</td>
                <td>
                    <button class="btn-danger" onclick="deleteEmployee(${emp.id})">Eliminar</button>
                </td>
            `;
            els.employeesTableBody.appendChild(tr);
        });
    }

    // --- ACTIONS ---

    async function toggleVacation(empId, dateStr, cell) {
        const isVacation = cell.classList.contains('vacation');

        // Optimistic update
        cell.classList.toggle('vacation');
        cell.textContent = isVacation ? '' : 'X';

        try {
            const res = await fetch('/api/vacations/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ employee_id: empId, date: dateStr })
            });

            if (!res.ok) throw new Error();

            // Update local state
            if (!isVacation) {
                state.vacations.push({ employee_id: empId, date: dateStr });
            } else {
                state.vacations = state.vacations.filter(v =>
                    !(v.employee_id === empId && v.date.startsWith(dateStr))
                );
            }
            showToast('Guardado');
        } catch (err) {
            // Revert
            cell.classList.toggle('vacation');
            cell.textContent = isVacation ? 'X' : '';
            alert('Error al guardar');
        }
    }

    async function handleRangeSubmit(e) {
        e.preventDefault();
        const data = {
            employee_id: els.rangeEmployee.value,
            start_date: document.getElementById('range-start').value,
            end_date: document.getElementById('range-end').value,
            type: document.getElementById('range-type').value
        };

        try {
            const res = await fetch('/api/vacations/range', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                els.modalRange.classList.add('hidden');
                loadQuadrantData();
                showToast('Rango añadido');
            }
        } catch (err) {
            alert('Error');
        }
    }

    async function handleTeamSubmit(e) {
        e.preventDefault();
        const data = {
            name: document.getElementById('team-name').value,
            description: document.getElementById('team-desc').value
        };

        try {
            const res = await fetch('/api/teams', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                els.modalTeam.classList.add('hidden');
                loadTeams();
                showToast('Equipo creado');
                e.target.reset();
            }
        } catch (err) {
            alert('Error');
        }
    }

    async function handleEmployeeSubmit(e) {
        e.preventDefault();
        const data = {
            name: document.getElementById('emp-name').value,
            role: document.getElementById('emp-role').value,
            team_id: document.getElementById('emp-team').value
        };

        try {
            const res = await fetch('/api/employees', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                els.modalEmployee.classList.add('hidden');
                loadAllEmployees();
                showToast('Empleado creado');
                e.target.reset();
            }
        } catch (err) {
            alert('Error');
        }
    }

    // --- HELPERS ---

    function createCell(html, className) {
        const div = document.createElement('div');
        div.className = className;
        div.innerHTML = html;
        els.calendarGrid.appendChild(div);
        return div;
    }

    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    function showToast(msg) {
        els.toast.textContent = msg;
        els.toast.classList.remove('hidden');
        setTimeout(() => els.toast.classList.add('hidden'), 2000);
    }

    function openModal(modal) {
        modal.classList.remove('hidden');
    }

    function openRangeModal() {
        // Populate employees select based on current team
        els.rangeEmployee.innerHTML = '';
        // We need the employees for the current team, which we fetched in loadQuadrantData
        // But we didn't save them globally. Let's fetch again or use state if we had it.
        // Better: fetch employees for current team
        fetch(`/api/employees?team_id=${state.currentTeamId}`)
            .then(res => res.json())
            .then(emps => {
                emps.forEach(emp => {
                    const opt = document.createElement('option');
                    opt.value = emp.id;
                    opt.textContent = emp.name;
                    els.rangeEmployee.appendChild(opt);
                });
                openModal(els.modalRange);
            });
    }

    function populateTeamSelect(selectEl) {
        selectEl.innerHTML = '';
        state.teams.forEach(team => {
            const opt = document.createElement('option');
            opt.value = team.id;
            opt.textContent = team.name;
            selectEl.appendChild(opt);
        });
    }

    // Global functions for onclick
    window.deleteTeam = async (id) => {
        if (!confirm('¿Seguro?')) return;
        await fetch(`/api/teams/${id}`, { method: 'DELETE' });
        loadTeams();
    };

    window.deleteEmployee = async (id) => {
        if (!confirm('¿Seguro?')) return;
        await fetch(`/api/employees/${id}`, { method: 'DELETE' });
        loadAllEmployees();
    };
});
