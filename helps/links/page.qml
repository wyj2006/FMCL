import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    GroupBox {
        title: qsTr("Minecraft")
        ColumnLayout {
            anchors.fill: parent
            Button {
                id: mcofficial
                text: qsTr("官网")
                onClicked: {
                    Qt.openUrlExternally("https://www.minecraft.net/");
                }
            }
            Button {
                id: wiki
                text: qsTr("Minecraft Wiki")
                onClicked: {
                    Qt.openUrlExternally("https://minecraft.wiki/");
                }
            }
            Button {
                id: mcmod
                text: qsTr("MC 百科")
                onClicked: {
                    Qt.openUrlExternally("https://www.mcmod.cn/");
                }
            }
            Button {
                id: plugin
                text: qsTr("插件百科")
                onClicked: {
                    Qt.openUrlExternally("https://mineplugin.org/");
                }
            }
            Button {
                id: modrinth
                text: qsTr("Modrinth")
                onClicked: {
                    Qt.openUrlExternally("https://modrinth.com/");
                }
            }
            Button {
                id: curseforge
                text: qsTr("Curseforge")
                onClicked: {
                    Qt.openUrlExternally("https://www.curseforge.com/minecraft/");
                }
            }
        }
    }
    GroupBox {
        title: qsTr("Java")
        ColumnLayout {
            anchors.fill: parent
            Button {
                id: javaofficial
                text: qsTr("官网")
                onClicked: {
                    Qt.openUrlExternally("https://www.java.com/");
                }
            }
            Button {
                id: openjdk
                text: qsTr("OpenJDK")
                onClicked: {
                    Qt.openUrlExternally("https://openjdk.org/");
                }
            }
            Button {
                id: dragonwell
                text: qsTr("Dragonwell")
                onClicked: {
                    Qt.openUrlExternally("https://dragonwell-jdk.io/");
                }
            }
            Button {
                id: azul
                text: qsTr("Azul")
                onClicked: {
                    Qt.openUrlExternally("https://www.azul.com/");
                }
            }
            Button {
                id: graalvm
                text: qsTr("GraalVM")
                onClicked: {
                    Qt.openUrlExternally("https://www.graalvm.org/");
                }
            }
        }
    }
}
