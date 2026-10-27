import { useEffect, useState } from "react";

const API = "http://localhost:5000";

function AIAnalysis() {

  const [stats, setStats] =
    useState(null);

  const loadStatistics =
    async () => {

      try {

        const response =
          await fetch(
            `${API}/api/statistics`
          );

        setStats(
          await response.json()
        );

      } catch (error) {

        console.error(error);

      }

    };


  useEffect(() => {

    loadStatistics();

    const interval =
      setInterval(
        loadStatistics,
        1000
      );

    return () =>
      clearInterval(interval);

  }, []);


  return (

    <div className="page">

      <div className="page-header">

        <div>

          <h1>AI Analysis</h1>

          <p>
            Live CNN prediction analytics
          </p>

        </div>

      </div>


      <div className="stats-grid">

        <div className="stat-card">

          <span>Total Predictions</span>

          <strong>
            {stats?.total_predictions ??
              0}
          </strong>

        </div>


        <div className="stat-card">

          <span>Drowning</span>

          <strong className="text-danger">

            {stats?.total_drowning ??
              0}

          </strong>

        </div>


        <div className="stat-card">

          <span>Non-Drowning</span>

          <strong className="text-success">

            {stats?.total_safe ??
              0}

          </strong>

        </div>


        <div className="stat-card">

          <span>Drowning Percentage</span>

          <strong className="text-danger">

            {stats?.drowning_percentage ??
              0}%

          </strong>

        </div>

      </div>


      <div className="card">

        <div className="card-header">

          <div>

            <h2>Prediction Distribution</h2>

            <p>
              Calculated from actual CNN predictions
            </p>

          </div>

        </div>


        <div className="prediction-details">

          <div className="detail-row">

            <span>
              Drowning
            </span>

            <strong>
              {stats?.drowning_percentage ??
                0}%
            </strong>

          </div>


          <div className="detail-row">

            <span>
              Non-Drowning
            </span>

            <strong>
              {stats?.safe_percentage ??
                0}%
            </strong>

          </div>

        </div>

      </div>


      <div className="card">

        <div className="card-header">

          <div>

            <h2>Recent AI Predictions</h2>

            <p>
              Latest model decisions
            </p>

          </div>

        </div>


        {stats?.prediction_history?.length ? (

          stats.prediction_history
            .slice(-20)
            .reverse()
            .map(
              (prediction, index) => (

                <div
                  className="detail-row"
                  key={index}
                >

                  <span>

                    {prediction.label}

                  </span>

                  <strong>

                    {prediction.confidence}%

                  </strong>

                </div>

              )
            )

        ) : (

          <div className="empty-state">

            Start monitoring to generate
            prediction analytics.

          </div>

        )}

      </div>

    </div>

  );
}

export default AIAnalysis;