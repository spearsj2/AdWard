// header for connecting to the server application
#ifndef ADWARDAPI_H
#define ADWARDAPI_H

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>

class adwardAPI : public QObject {
    Q_OBJECT
public:
    explicit adwardAPI(QObject *parent = nullptr);
    void fetchSummary(const QString &apiUrl, const QString &apiKey);

private:
    QNetworkAccessManager *networkManager;

private slots:
    void onNetworkReply(QNetworkReply *reply);
};

#endif
