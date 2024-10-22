#include <QApplication>
#include "frontPage.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    frontPage window;
    window.show();
    return app.exec();
}
