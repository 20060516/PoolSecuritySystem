import { useEffect, useState } from "react";

const API = "http://localhost:5000";

function Settings() {

  const [settings, setSettings] =
    useState(null);

  const [saved, setSaved] =
    useState(false);


  useEffect(() => {

    fetch(`${API}/api/settings`)
      .then(response =>
        response.json()
      )
      .then(data =>
        setSettings(data)
      )
      .catch(error =>
        console.error(error)
      );

  }, []);


  if (!settings) {

    return (
      <div className="page">

        <h1>Settings</h1>

        <p>Loading settings...</p>

      </div>
    );
  }


  const saveSettings = () => {

    localStorage.setItem(
      "aquaguard_settings",
      JSON.stringify(settings)
    );

    setSaved(true);

    setTimeout(
      () => setSaved(false),
      2000
    );

  };


  return (

    <div className="page">

      <div className="page-header">

        <div>

          <h1>Settings</h1>

          <p>
            AquaGuard monitoring configuration
          </p>

        </div>

      </div>


      <div className="card">

        <h2>AI Monitoring</h2>


        <div className="form-group">

          <label>
            Emergency Detection Frames
          </label>

          <input
            type="number"
            min="1"
            value={
              settings.emergency_frames
            }
            onChange={e =>
              setSettings({
                ...settings,
                emergency_frames:
                  Number(e.target.value)
              })
            }
          />

          <small>
            Number of consecutive drowning
            predictions required to confirm
            an emergency.
          </small>

        </div>


        <div className="detail-row">

          <span>Model</span>

          <strong>
            {settings.model}
          </strong>

        </div>


        <div className="detail-row">

          <span>Input Size</span>

          <strong>
            {settings.image_size}
          </strong>

        </div>

      </div>


      <div className="card">

        <h2>Video Source</h2>


        <div className="detail-row">

          <span>Current Source</span>

          <strong>
            {settings.video_source}
          </strong>

        </div>

      </div>


      <div className="card">

        <h2>IoT Configuration</h2>


        <div className="detail-row">

          <span>Device</span>

          <strong>
            {settings.iot}
          </strong>

        </div>


        <div className="detail-row">

          <span>Notification</span>

          <strong>
            {settings.notification}
          </strong>

        </div>

      </div>


      <button
        className="btn btn-primary"
        onClick={saveSettings}
      >

        Save Settings

      </button>


      {saved && (

        <p className="text-success">

          Settings saved successfully.

        </p>

      )}

    </div>

  );
}

export default Settings;