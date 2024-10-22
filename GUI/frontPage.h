#ifndef FRONTPAGE_H
#define FRONTPAGE_H

#include <QMainWindow>
#include <QPushButton>
#include <QNetworkAccessManager>

class frontPage : public QMainWindow {
    Q_OBJECT

public:
    frontPage(QWidget *parent = nullptr);
    ~frontPage();

private slots:
    void toggleAdWard();
    void disableAdWard();
    void enableAdWard();

private:
    QPushButton *toggleButton;
    QNetworkAccessManager *networkManager;
};

#endif
