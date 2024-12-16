#include <QMainWindow>
#include <QPushButton>
#include <QDialog>
#include <QListWidget>
#include <QLineEdit>
#include <QVBoxLayout>
#include <QNetworkAccessManager>

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void showBlocklistModal();
    void showAllowlistModal();
    void addToBlocklist();
    void addToAllowlist();
    void fetchBlocklist();
    void fetchAllowlist();

private:
    QPushButton *blocklistButton;
    QPushButton *allowlistButton;
    QNetworkAccessManager *networkManager;

    QDialog *blocklistModal;
    QDialog *allowlistModal;

    QListWidget *blocklistView;
    QListWidget *allowlistView;

    QLineEdit *blocklistInput;
    QLineEdit *allowlistInput;
};

#endif // MAINWINDOW_H
