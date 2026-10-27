import { useEffect, useState } from "react";

const API = "http://localhost:5000";

function IncidentHistory() {

  const [incidents, setIncidents] =
    useState([]);

  const loadIncidents =
    async () => {

      try {

        const response =
          await fetch(
            `${API}/api/incidents`
          );

        setIncidents(
          await response.json()
        );

      } catch (error) {

        console.error(error);

      }

    };


  useEffect(() => {

    loadIncidents();

    const interval =
      setInterval(
        loadIncidents,
        2000
      );

    return () =>
      clearInterval(interval);

  }, []);


  return (

    <div className="page">

      <div className="page-header">

        <div>

          <h1>Incident History</h1>

          <p>
            Previously confirmed drowning incidents
          </p>

        </div>

      </div>


      <div className="card">

        {incidents.length === 0 ? (

          <div className="empty-state">

            No confirmed incidents yet.

            <br />

            Incidents will appear here after
            an emergency is confirmed and reset.

          </div>

        ) : (

          <div className="table-container">

            <table>

              <thead>

                <tr>

                  <th>ID</th>

                  <th>Date & Time</th>

                  <th>Confidence</th>

                  <th>Duration</th>

                  <th>Alarm</th>

                  <th>IoT</th>

                  <th>Status</th>

                </tr>

              </thead>


              <tbody>

                {incidents.map(
                  incident => (

                    <tr
                      key={incident.id}
                    >

                      <td>
                        #{incident.id}
                      </td>

                      <td>
                        {new Date(
                          incident.timestamp
                        ).toLocaleString()}
                      </td>

                      <td>
                        {incident.confidence}%
                      </td>

                      <td>
                        {incident.duration}s
                      </td>

                      <td>
                        {incident.alarm}
                      </td>

                      <td>
                        {incident.iot}
                      </td>

                      <td>
                        {incident.status}
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>

  );
}

export default IncidentHistory;