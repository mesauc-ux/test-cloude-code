/*
 * Ders Programı Yönetim Sistemi - JavaScript
 * Course Schedule Management System - Main JavaScript
 */

// Global state
let currentTab = 'teachers';
let scheduleData = null;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupTabNavigation();
    setupDarkMode();
    setupEventListeners();
    loadTeachers();
    loadStudents();
}

// ============= TAB NAVIGATION =============

function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');

    currentTab = tabName;

    // Load data for the tab
    if (tabName === 'saved') {
        loadSavedSchedules();
    }
}

// ============= DARK MODE =============

function setupDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const isDarkMode = localStorage.getItem('darkMode') === 'true';

    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        darkModeToggle.textContent = '☀️ Aydınlık Mod';
    }

    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        this.textContent = isDark ? '☀️ Aydınlık Mod' : '🌙 Karanlık Mod';
    });
}

// ============= EVENT LISTENERS =============

function setupEventListeners() {
    // Teacher buttons
    document.getElementById('addTeacherBtn').addEventListener('click', () => showTeacherModal());

    // Student buttons
    document.getElementById('addStudentBtn').addEventListener('click', () => showStudentModal());

    // Schedule buttons
    document.getElementById('generateScheduleBtn').addEventListener('click', generateSchedule);
    document.getElementById('saveScheduleBtn').addEventListener('click', saveSchedule);
    document.getElementById('exportExcelBtn').addEventListener('click', () => exportSchedule('excel'));
    document.getElementById('exportPdfBtn').addEventListener('click', () => exportSchedule('pdf'));
    document.getElementById('exportHtmlBtn').addEventListener('click', () => exportSchedule('html'));

    // Saved schedules
    document.getElementById('refreshSavedBtn').addEventListener('click', loadSavedSchedules);

    // Modal overlay
    document.getElementById('modalOverlay').addEventListener('click', closeModal);
}

// ============= TEACHERS =============

async function loadTeachers() {
    try {
        const response = await fetch('/teachers');
        const teachers = await response.json();

        const teachersList = document.getElementById('teachersList');
        teachersList.innerHTML = '';

        if (teachers.length === 0) {
            teachersList.innerHTML = '<p class="placeholder-text">Henüz öğretmen eklenmemiş.</p>';
            return;
        }

        teachers.forEach(teacher => {
            const teacherEl = createTeacherElement(teacher);
            teachersList.appendChild(teacherEl);
        });
    } catch (error) {
        console.error('Error loading teachers:', error);
        showNotification('Öğretmenler yüklenirken hata oluştu', 'error');
    }
}

function createTeacherElement(teacher) {
    const div = document.createElement('div');
    div.className = 'data-item';
    div.innerHTML = `
        <div class="data-item-info">
            <h3>${teacher.name} ${teacher.surname}</h3>
            <p>Branş: ${teacher.branch}</p>
        </div>
        <div class="data-item-actions">
            <button class="btn btn-secondary btn-sm" onclick="editTeacher(${teacher.id})">✏️ Düzenle</button>
            <button class="btn btn-danger btn-sm" onclick="deleteTeacher(${teacher.id})">🗑️ Sil</button>
        </div>
    `;
    return div;
}

function showTeacherModal(teacher = null) {
    const isEdit = teacher !== null;
    const modalHTML = `
        <h2>${isEdit ? 'Öğretmen Düzenle' : 'Yeni Öğretmen Ekle'}</h2>
        <form id="teacherForm">
            <div class="form-group">
                <label>Ad:</label>
                <input type="text" name="name" value="${teacher?.name || ''}" required>
            </div>
            <div class="form-group">
                <label>Soyad:</label>
                <input type="text" name="surname" value="${teacher?.surname || ''}" required>
            </div>
            <div class="form-group">
                <label>Branş:</label>
                <input type="text" name="branch" value="${teacher?.branch || ''}" required>
            </div>
            <div class="form-group">
                <button type="submit" class="btn btn-primary">${isEdit ? 'Güncelle' : 'Ekle'}</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">İptal</button>
            </div>
        </form>
    `;

    showModal(modalHTML);

    document.getElementById('teacherForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            surname: formData.get('surname'),
            branch: formData.get('branch'),
            schedule: '{}'
        };

        try {
            const url = isEdit ? `/teachers/${teacher.id}` : '/teachers';
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                closeModal();
                loadTeachers();
                showNotification('Öğretmen kaydedildi', 'success');
            }
        } catch (error) {
            console.error('Error saving teacher:', error);
            showNotification('Kaydetme işlemi başarısız', 'error');
        }
    });
}

async function editTeacher(id) {
    // TODO: Implement edit teacher
    showNotification('Düzenleme özelliği yakında eklenecek', 'info');
}

async function deleteTeacher(id) {
    if (!confirm('Bu öğretmeni silmek istediğinizden emin misiniz?')) {
        return;
    }

    try {
        const response = await fetch(`/teachers/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadTeachers();
            showNotification('Öğretmen silindi', 'success');
        }
    } catch (error) {
        console.error('Error deleting teacher:', error);
        showNotification('Silme işlemi başarısız', 'error');
    }
}

// ============= STUDENTS =============

async function loadStudents() {
    try {
        const response = await fetch('/students');
        const students = await response.json();

        const studentsList = document.getElementById('studentsList');
        studentsList.innerHTML = '';

        if (students.length === 0) {
            studentsList.innerHTML = '<p class="placeholder-text">Henüz öğrenci eklenmemiş.</p>';
            return;
        }

        students.forEach(student => {
            const studentEl = createStudentElement(student);
            studentsList.appendChild(studentEl);
        });
    } catch (error) {
        console.error('Error loading students:', error);
        showNotification('Öğrenciler yüklenirken hata oluştu', 'error');
    }
}

function createStudentElement(student) {
    const div = document.createElement('div');
    div.className = 'data-item';
    div.innerHTML = `
        <div class="data-item-info">
            <h3>${student.name} ${student.surname}</h3>
            <p>Sınıf: ${student.class}</p>
        </div>
        <div class="data-item-actions">
            <button class="btn btn-secondary btn-sm" onclick="editStudent(${student.id})">✏️ Düzenle</button>
            <button class="btn btn-danger btn-sm" onclick="deleteStudent(${student.id})">🗑️ Sil</button>
        </div>
    `;
    return div;
}

function showStudentModal(student = null) {
    const isEdit = student !== null;
    const modalHTML = `
        <h2>${isEdit ? 'Öğrenci Düzenle' : 'Yeni Öğrenci Ekle'}</h2>
        <form id="studentForm">
            <div class="form-group">
                <label>Ad:</label>
                <input type="text" name="name" value="${student?.name || ''}" required>
            </div>
            <div class="form-group">
                <label>Soyad:</label>
                <input type="text" name="surname" value="${student?.surname || ''}" required>
            </div>
            <div class="form-group">
                <label>Sınıf:</label>
                <input type="text" name="class" value="${student?.class || ''}" required>
            </div>
            <div class="form-group">
                <button type="submit" class="btn btn-primary">${isEdit ? 'Güncelle' : 'Ekle'}</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">İptal</button>
            </div>
        </form>
    `;

    showModal(modalHTML);

    document.getElementById('studentForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            surname: formData.get('surname'),
            class: formData.get('class')
        };

        try {
            const url = isEdit ? `/students/${student.id}` : '/students';
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                closeModal();
                loadStudents();
                showNotification('Öğrenci kaydedildi', 'success');
            }
        } catch (error) {
            console.error('Error saving student:', error);
            showNotification('Kaydetme işlemi başarısız', 'error');
        }
    });
}

async function editStudent(id) {
    // TODO: Implement edit student
    showNotification('Düzenleme özelliği yakında eklenecek', 'info');
}

async function deleteStudent(id) {
    if (!confirm('Bu öğrenciyi silmek istediğinizden emin misiniz?')) {
        return;
    }

    try {
        const response = await fetch(`/students/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadStudents();
            showNotification('Öğrenci silindi', 'success');
        }
    } catch (error) {
        console.error('Error deleting student:', error);
        showNotification('Silme işlemi başarısız', 'error');
    }
}

// ============= SCHEDULE =============

async function generateSchedule() {
    const scheduleDisplay = document.getElementById('scheduleDisplay');
    scheduleDisplay.innerHTML = '<div class="spinner"></div><p style="text-align: center;">Program oluşturuluyor...</p>';

    try {
        const response = await fetch('/generate_schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        scheduleData = await response.json();
        displaySchedule(scheduleData);
        showNotification('Program oluşturuldu', 'success');
    } catch (error) {
        console.error('Error generating schedule:', error);
        scheduleDisplay.innerHTML = '<p class="placeholder-text" style="color: red;">Program oluşturulurken hata oluştu</p>';
        showNotification('Program oluşturulamadı', 'error');
    }
}

function displaySchedule(data) {
    const scheduleDisplay = document.getElementById('scheduleDisplay');
    // TODO: Implement actual schedule display
    scheduleDisplay.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <p><strong>Durum:</strong> ${data.status}</p>
            <p>${data.message}</p>
            <p style="color: #999; margin-top: 20px;">
                ℹ️ Tam ders programı görüntüleme özelliği orijinal koddan eklenecek
            </p>
        </div>
    `;
}

async function saveSchedule() {
    if (!scheduleData) {
        showNotification('Kaydedilecek program bulunamadı', 'warning');
        return;
    }

    const name = prompt('Program adı girin:');
    if (!name) return;

    try {
        const response = await fetch('/save_schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            showNotification('Program kaydedildi', 'success');
        }
    } catch (error) {
        console.error('Error saving schedule:', error);
        showNotification('Kaydetme başarısız', 'error');
    }
}

async function exportSchedule(format) {
    if (!scheduleData) {
        showNotification('Dışa aktarılacak program bulunamadı', 'warning');
        return;
    }

    try {
        const response = await fetch(`/export/${format}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scheduleData)
        });

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ders_programi.${format === 'excel' ? 'xlsx' : format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        showNotification('Dosya indiriliyor', 'success');
    } catch (error) {
        console.error('Error exporting:', error);
        showNotification('Dışa aktarma başarısız', 'error');
    }
}

// ============= SAVED SCHEDULES =============

async function loadSavedSchedules() {
    try {
        const response = await fetch('/saved_schedules');
        const schedules = await response.json();

        const savedList = document.getElementById('savedSchedulesList');
        savedList.innerHTML = '';

        if (schedules.length === 0) {
            savedList.innerHTML = '<p class="placeholder-text">Henüz kaydedilmiş program yok.</p>';
            return;
        }

        schedules.forEach(schedule => {
            const scheduleEl = createSavedScheduleElement(schedule);
            savedList.appendChild(scheduleEl);
        });
    } catch (error) {
        console.error('Error loading saved schedules:', error);
        showNotification('Programlar yüklenemedi', 'error');
    }
}

function createSavedScheduleElement(schedule) {
    const div = document.createElement('div');
    div.className = 'data-item';
    const date = new Date(schedule.created_at).toLocaleString('tr-TR');
    div.innerHTML = `
        <div class="data-item-info">
            <h3>${schedule.name}</h3>
            <p>Oluşturulma: ${date}</p>
        </div>
        <div class="data-item-actions">
            <button class="btn btn-secondary btn-sm" onclick="loadSavedSchedule(${schedule.id})">📂 Yükle</button>
            <button class="btn btn-danger btn-sm" onclick="deleteSavedSchedule(${schedule.id})">🗑️ Sil</button>
        </div>
    `;
    return div;
}

async function loadSavedSchedule(id) {
    try {
        const response = await fetch(`/saved_schedules/${id}`);
        const data = await response.json();

        if (data.success) {
            scheduleData = data.schedule;
            switchTab('schedule');
            displaySchedule(scheduleData);
            showNotification('Program yüklendi', 'success');
        }
    } catch (error) {
        console.error('Error loading schedule:', error);
        showNotification('Program yüklenemedi', 'error');
    }
}

async function deleteSavedSchedule(id) {
    if (!confirm('Bu programı silmek istediğinizden emin misiniz?')) {
        return;
    }

    try {
        const response = await fetch(`/saved_schedules/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadSavedSchedules();
            showNotification('Program silindi', 'success');
        }
    } catch (error) {
        console.error('Error deleting schedule:', error);
        showNotification('Silme başarısız', 'error');
    }
}

// ============= MODAL =============

function showModal(html) {
    const modal = document.getElementById('modalContainer');
    const overlay = document.getElementById('modalOverlay');

    modal.innerHTML = html;
    modal.classList.add('active');
    overlay.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('modalContainer');
    const overlay = document.getElementById('modalOverlay');

    modal.classList.remove('active');
    overlay.classList.remove('active');
}

// ============= NOTIFICATIONS =============

function showNotification(message, type = 'info') {
    // Simple console log for now
    // TODO: Implement toast notifications
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}
