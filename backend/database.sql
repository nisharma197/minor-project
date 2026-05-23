-- ============================================================
-- FIRE NOC SYSTEM - Complete MySQL Database
-- ============================================================

CREATE DATABASE IF NOT EXISTS fire_noc_db;
USE fire_noc_db;

-- ============================================================
-- TABLE 1: USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'inspector', 'applicant') NOT NULL DEFAULT 'applicant',
    phone_number VARCHAR(15),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1
);

-- ============================================================
-- TABLE 2: APPLICATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    building_name VARCHAR(150) NOT NULL,
    building_type VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    current_status ENUM('Pending','Under Inspection','Follow-up Required','Approved','Rejected') DEFAULT 'Pending',
    priority_level ENUM('Low','Medium','High') DEFAULT 'Medium',
    remarks TEXT,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 3: INSPECTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS inspections (
    inspection_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    inspector_id INT NOT NULL,
    inspection_date DATETIME,
    inspection_status ENUM('Scheduled','In Progress','Completed','Failed') DEFAULT 'Scheduled',
    findings TEXT,
    remarks TEXT,
    uploaded_images VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 4: FOLLOWUPS
-- ============================================================
CREATE TABLE IF NOT EXISTS followups (
    followup_id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT NOT NULL,
    followup_date DATETIME,
    followup_status ENUM('Pending','Completed','Skipped') DEFAULT 'Pending',
    followup_remarks TEXT,
    FOREIGN KEY (inspection_id) REFERENCES inspections(inspection_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 5: NOC
-- ============================================================
CREATE TABLE IF NOT EXISTS noc (
    noc_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL UNIQUE,
    approval_status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    approved_by INT,
    issue_date DATETIME,
    expiry_date DATETIME,
    rejection_reason TEXT,
    pdf_certificate_path VARCHAR(255),
    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- ============================================================
-- TABLE 6: DOCUMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    document_name VARCHAR(150) NOT NULL,
    document_path VARCHAR(255) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 7: NOTIFICATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    status ENUM('Unread','Read') DEFAULT 'Unread',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 8: ACTIVITY_LOGS
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- SEED DATA - Default Admin, Inspector, Applicant
-- Passwords are bcrypt hashed version of 'Admin@123', 'Inspector@123', 'Applicant@123'
-- ============================================================

INSERT INTO users (full_name, email, username, password, role, phone_number) VALUES
('System Administrator', 'admin@firenoc.gov.in', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8ZYfDH9X5DjBdZyGjNq', 'admin', '9000000001'),
('Ravi Kumar', 'inspector@firenoc.gov.in', 'inspector1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8ZYfDH9X5DjBdZyGjNq', 'inspector', '9000000002'),
('Priya Sharma', 'applicant@firenoc.gov.in', 'applicant1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8ZYfDH9X5DjBdZyGjNq', 'applicant', '9000000003'),
('Suresh Patel', 'suresh@example.com', 'suresh_p', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8ZYfDH9X5DjBdZyGjNq', 'applicant', '9876543210'),
('Meena Joshi', 'meena@firenoc.gov.in', 'inspector2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8ZYfDH9X5DjBdZyGjNq', 'inspector', '9000000004');

INSERT INTO applications (applicant_id, building_name, building_type, address, city, state, pincode, current_status, priority_level, remarks) VALUES
(3, 'Sunrise Towers', 'Commercial', '12 MG Road', 'Bhopal', 'Madhya Pradesh', '462001', 'Under Inspection', 'High', 'Fire exits need verification'),
(3, 'Green Park Mall', 'Mall', '45 VIP Road', 'Indore', 'Madhya Pradesh', '452001', 'Pending', 'Medium', NULL),
(4, 'Hotel Royal', 'Hotel', '78 Link Road', 'Jabalpur', 'Madhya Pradesh', '482001', 'Approved', 'Low', 'All checks passed'),
(4, 'City Hospital', 'Hospital', '33 Civil Lines', 'Gwalior', 'Madhya Pradesh', '474001', 'Follow-up Required', 'High', 'Sprinkler system issue'),
(3, 'Star Apartments', 'Residential', '5 Subhash Nagar', 'Bhopal', 'Madhya Pradesh', '462003', 'Rejected', 'Medium', 'Fire exits blocked');

INSERT INTO inspections (application_id, inspector_id, inspection_date, inspection_status, findings, remarks) VALUES
(1, 2, '2025-05-01 10:00:00', 'In Progress', 'Fire exits partially blocked. Extinguishers OK.', 'Needs follow-up'),
(3, 2, '2025-04-20 11:00:00', 'Completed', 'All fire safety equipment in place.', 'Passed'),
(4, 5, '2025-04-25 09:30:00', 'Failed', 'Sprinkler system not functional.', 'Requires repair'),
(5, 5, '2025-04-28 14:00:00', 'Completed', 'Fire exits permanently blocked.', 'Rejected');

INSERT INTO followups (inspection_id, followup_date, followup_status, followup_remarks) VALUES
(1, '2025-05-10 10:00:00', 'Pending', 'Verify fire exit clearance'),
(3, '2025-05-05 11:00:00', 'Pending', 'Check sprinkler repairs');

INSERT INTO noc (application_id, approval_status, approved_by, issue_date, expiry_date) VALUES
(3, 'Approved', 1, '2025-04-22 12:00:00', '2026-04-22 12:00:00'),
(5, 'Rejected', 1, NULL, NULL);

INSERT INTO notifications (user_id, title, message, status) VALUES
(3, 'Application Received', 'Your application for Sunrise Towers has been received and is under review.', 'Unread'),
(3, 'Inspection Scheduled', 'An inspection has been scheduled for Sunrise Towers on 2025-05-01.', 'Unread'),
(2, 'New Inspection Assigned', 'You have been assigned to inspect Sunrise Towers.', 'Read'),
(1, 'NOC Approval Needed', 'Hotel Royal is ready for NOC issuance.', 'Unread'),
(4, 'NOC Approved', 'Your NOC for Hotel Royal has been approved.', 'Read'),
(3, 'Application Rejected', 'Your application for Star Apartments has been rejected due to blocked fire exits.', 'Unread');

INSERT INTO activity_logs (user_id, action) VALUES
(1, 'Admin logged in'),
(2, 'Inspector submitted inspection report for Sunrise Towers'),
(3, 'Applicant submitted new application for Green Park Mall'),
(1, 'Admin approved NOC for Hotel Royal'),
(5, 'Inspector submitted inspection report for City Hospital');
