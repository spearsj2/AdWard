// declaration for connecting to the server app
#include "adwardAPI.h"
#include <QNetworkRequest>
#include <QUrl>

adwardAPI::adwardAPI(QObject *parent) : QObject(parent) {
    networkManager = new QNetworkAccessManager(this);
    connect(networkManager, &QNetworkAccessManager::finished, this, &PiHoleAPI::onNetworkReply);
}

void adwardAPI::fetchSummary(const QString &apiUrl, const QString &apiKey) {
    QUrl url(apiUrl + "/admin/api.php?summaryRaw&auth=" + apiKey);
    QNetworkRequest request(url);
    networkManager->get(request);
}

void adwardAPI::onNetworkReply(QNetworkReply *reply) {
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        QJsonDocument jsonResponse = QJsonDocument::fromJson(response);
        QJsonObject jsonObject = jsonResponse.object();
        
        qDebug() << "Response Summary:" << jsonObject;
    } else {
        qDebug() << "Error fetching data:" << reply->errorString();
    }
    reply->deleteLater();
}
