/****************************************************************************
** Meta object code from reading C++ file 'ManualControl.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.12.8)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../../src/lss_gcs/rviz_plugin/include/ManualControl.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'ManualControl.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.12.8. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_ManualControl_t {
    QByteArrayData data[10];
    char stringdata0[92];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_ManualControl_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_ManualControl_t qt_meta_stringdata_ManualControl = {
    {
QT_MOC_LITERAL(0, 0, 13), // "ManualControl"
QT_MOC_LITERAL(1, 14, 6), // "setVel"
QT_MOC_LITERAL(2, 21, 0), // ""
QT_MOC_LITERAL(3, 22, 5), // "speed"
QT_MOC_LITERAL(4, 28, 5), // "servo"
QT_MOC_LITERAL(5, 34, 22), // "overrideButtonCallback"
QT_MOC_LITERAL(6, 57, 8), // "setTopic"
QT_MOC_LITERAL(7, 66, 5), // "topic"
QT_MOC_LITERAL(8, 72, 7), // "sendVel"
QT_MOC_LITERAL(9, 80, 11) // "updateTopic"

    },
    "ManualControl\0setVel\0\0speed\0servo\0"
    "overrideButtonCallback\0setTopic\0topic\0"
    "sendVel\0updateTopic"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_ManualControl[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       5,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    2,   39,    2, 0x0a /* Public */,
       5,    0,   44,    2, 0x0a /* Public */,
       6,    1,   45,    2, 0x0a /* Public */,
       8,    0,   48,    2, 0x09 /* Protected */,
       9,    0,   49,    2, 0x09 /* Protected */,

 // slots: parameters
    QMetaType::Void, QMetaType::Float, QMetaType::Float,    3,    4,
    QMetaType::Void,
    QMetaType::Void, QMetaType::QString,    7,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

void ManualControl::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<ManualControl *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->setVel((*reinterpret_cast< float(*)>(_a[1])),(*reinterpret_cast< float(*)>(_a[2]))); break;
        case 1: _t->overrideButtonCallback(); break;
        case 2: _t->setTopic((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 3: _t->sendVel(); break;
        case 4: _t->updateTopic(); break;
        default: ;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject ManualControl::staticMetaObject = { {
    &rviz::Panel::staticMetaObject,
    qt_meta_stringdata_ManualControl.data,
    qt_meta_data_ManualControl,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *ManualControl::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *ManualControl::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_ManualControl.stringdata0))
        return static_cast<void*>(this);
    return rviz::Panel::qt_metacast(_clname);
}

int ManualControl::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = rviz::Panel::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 5)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 5;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 5)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 5;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
