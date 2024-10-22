#include "frontPage.h"
#include <QVBoxLayout>
#include <QNetworkRequest>
#include <QUrl>

MainWindow::frontPage(QWidget *parent)
    : QMainWindow(parent), networkManager(new QNetworkAccessManager(this)) {

    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *layout = new QVBoxLayout();

    // switch to turn the server connection off and on
    toggleButton = new QPushButton("Cut Server connection", this);
    toggleButton->setCheckable(true);
    layout->addWidget(toggleButton);

    connect(toggleButton, &QPushButton::clicked, this, &MainWindow::togglePiHole);

    centralWidget->setLayout(layout);
    setCentralWidget(centralWidget);
    setWindowTitle("AdWard Connection Toggle");
}

frontPage::~frontPage() {
    // Qt here shouldautomatically deletes child objects
}

void frontPage::toggleAdWard() {
    if (toggleButton->isChecked()) {
        toggleButton->setText("Enable AdWard");
        disableAdWard();
    } else {
        toggleButton->setText("Disable AdWard");
        enableAdWard();
    }
}

void MainWindow::disableAdWard() {
    // Replace with the server api and token
    QString url = "URL to connect to the serve";
    QNetworkRequest request(QUrl(url));
    networkManager->get(request);
}

void MainWindow::enableAdWard() {
    // Replace with your actual Pi-hole API and token
    QString url = "URL to connect to the Server";
    QNetworkRequest request(QUrl(url));
    networkManager->get(request);
}
