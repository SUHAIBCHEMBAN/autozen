function SettingsSection({ handleLogout }) {
  return (
    <div className="profile-section">
      <div className="section-header">
        <h2>Account Settings</h2>
      </div>
      <div className="settings-list">
        <div className="setting-item">
          <div className="setting-info">
            <h3>Notifications</h3>
            <p>Manage your email and push notifications</p>
          </div>
          <button className="btn-secondary">Manage</button>
        </div>
        <div className="setting-item">
          <div className="setting-info">
            <h3>Privacy</h3>
            <p>Control your privacy settings</p>
          </div>
          <button className="btn-secondary">Manage</button>
        </div>
        <div className="setting-item">
          <div className="setting-info">
            <h3>Security</h3>
            <p>Update your security preferences</p>
          </div>
          <button className="btn-secondary">Manage</button>
        </div>
        <div className="setting-item danger">
          <div className="setting-info">
            <h3>Logout</h3>
            <p>Sign out of your account</p>
          </div>
          <button className="btn-danger" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsSection