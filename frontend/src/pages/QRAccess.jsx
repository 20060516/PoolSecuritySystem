import { QRCodeCanvas } from "qrcode.react";

function QRAccess() {

  const publicUrl =
    window.location.origin;

  return (

    <div className="page">

      <div className="page-header">

        <div>

          <h1>QR Access</h1>

          <p>
            Quickly access AquaGuard from a mobile device.
          </p>

        </div>

      </div>


      <div className="card qr-card">

        <h2>
          AquaGuard Mobile Access
        </h2>

        <p>
          Scan this QR code to open the
          AquaGuard application.
        </p>


        <div className="qr-container">

          <QRCodeCanvas
            value={publicUrl}
            size={220}
            includeMargin
          />

        </div>


        <div className="detail-row">

          <span>Application URL</span>

          <strong>
            {publicUrl}
          </strong>

        </div>

      </div>

    </div>

  );
}

export default QRAccess;