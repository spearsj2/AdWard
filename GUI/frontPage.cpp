#include "frontPage.h"
#include <QVBoxLayout>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QUrl>
#include <QMessageBox>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), networkManager(new QNetworkAccessManager(this)) {

    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *layout = new QVBoxLayout();

    // Buttons for Blocklist and Allowlist
    blocklistButton = new QPushButton("Manage Blocklist", this);
    allowlistButton = new QPushButton("Manage Allowlist", this);

    layout->addWidget(blocklistButton);
    layout->addWidget(allowlistButton);

    connect(blocklistButton, &QPushButton::clicked, this, &MainWindow::showBlocklistModal);
    connect(allowlistButton, &QPushButton::clicked, this, &MainWindow::showAllowlistModal);

    centralWidget->setLayout(layout);
    setCentralWidget(centralWidget);
    setWindowTitle("Pi-hole Block/Allowlist Manager");
}

MainWindow::~MainWindow() {}

void MainWindow::showBlocklistModal() {
    blocklistModal = new QDialog(this);
    QVBoxLayout *modalLayout = new QVBoxLayout(blocklistModal);

    blocklistView = new QListWidget(blocklistModal);
    blocklistInput = new QLineEdit(blocklistModal);
    QPushButton *addButton = new QPushButton("Add to Blocklist", blocklistModal);

    modalLayout->addWidget(blocklistView);
    modalLayout->addWidget(blocklistInput);
    modalLayout->addWidget(addButton);

    connect(addButton, &QPushButton::clicked, this, &MainWindow::addToBlocklist);

    fetchBlocklist(); // Fetch and display the blocklist
    blocklistModal->setLayout(modalLayout);
    blocklistModal->setWindowTitle("Manage Blocklist");
    blocklistModal->exec();
}

void MainWindow::showAllowlistModal() {
    allowlistModal = new QDialog(this);
    QVBoxLayout *modalLayout = new QVBoxLayout(allowlistModal);

    allowlistView = new QListWidget(allowlistModal);
    allowlistInput = new QLineEdit(allowlistModal);
    QPushButton *addButton = new QPushButton("Add to Allowlist", allowlistModal);

    modalLayout->addWidget(allowlistView);
    modalLayout->addWidget(allowlistInput);
    modalLayout->addWidget(addButton);

    connect(addButton, &QPushButton::clicked, this, &MainWindow::addToAllowlist);

    fetchAllowlist(); // Fetch and display the allowlist
    allowlistModal->setLayout(modalLayout);
    allowlistModal->setWindowTitle("Manage Allowlist");
    allowlistModal->exec();
}

void MainWindow::addToBlocklist() {
    QString domain = blocklistInput->text();
    if (domain.isEmpty()) {
        QMessageBox::warning(this, "Error", "Domain cannot be empty.");
        return;
    }

    QString url = QString("http://your-pihole-ip/admin/api.php?list=black&add=%1&auth=your-api-token").arg(domain);
    QNetworkRequest request(QUrl(url));
    networkManager->get(request);
    QMessageBox::information(this, "Success", "Domain added to blocklist.");
}

void MainWindow::addToAllowlist() {
    QString domain = allowlistInput->text();
    if (domain.isEmpty()) {
        QMessageBox::warning(this, "Error", "Domain cannot be empty.");
        return;
    }

    QString url = QString("http://your-pihole-ip/admin/api.php?list=white&add=%1&auth=your-api-token").arg(domain);
    QNetworkRequest request(QUrl(url));
    networkManager->get(request);
    QMessageBox::information(this, "Success", "Domain added to allowlist.");
}

void MainWindow::fetchBlocklist() {
    QString url = "http://your-pihole-ip/admin/api.php?list=black&auth=your-api-token";
    QNetworkRequest request(QUrl(url));

    QNetworkReply *reply = networkManager->get(request);
    connect(reply, &QNetworkReply::finished, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QStringList domains = QString(reply->readAll()).split("\n");
            blocklistView->addItems(domains);
        } else {
            QMessageBox::critical(this, "Error", "Failed to fetch blocklist.");
        }
        reply->deleteLater();
    });
}

void MainWindow::fetchAllowlist() {
    QString url = "http://your-pihole-ip/admin/api.php?list=white&auth=your-api-token";
    QNetworkRequest request(QUrl(url));

    QNetworkReply *reply = networkManager->get(request);
    connect(reply, &QNetworkReply::finished, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QStringList domains = QString(reply->readAll()).split("\n");
            allowlistView->addItems(domains);
        } else {
            QMessageBox::critical(this, "Error", "Failed to fetch allowlist.");
        }
        reply->deleteLater();
    });
}
