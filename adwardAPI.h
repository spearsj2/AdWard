#ifndef PIHOLEAPI_H
#define PIHOLEAPI_H

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>

class PiHoleAPI : public QObject {
    Q_OBJECT
public:
    explicit PiHoleAPI(QObject *parent = nullptr);
    void fetchSummary(const QString &apiUrl, const QString &apiKey);

private:
    QNetworkAccessManager *networkManager;

private slots:
    void onNetworkReply(QNetworkReply *reply);
};

#endif
