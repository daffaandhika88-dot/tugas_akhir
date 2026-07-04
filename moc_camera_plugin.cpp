/****************************************************************************
** Meta object code from reading C++ file 'camera_plugin.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.12.8)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../../../src/lss_gcs/rviz_plugin/include/camera_plugin.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'camera_plugin.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.12.8. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_CameraPanel_t {
    QByteArrayData data[14];
    char stringdata0[175];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_CameraPanel_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_CameraPanel_t qt_meta_stringdata_CameraPanel = {
    {
QT_MOC_LITERAL(0, 0, 11), // "CameraPanel"
QT_MOC_LITERAL(1, 12, 15), // "critLineChanged"
QT_MOC_LITERAL(2, 28, 0), // ""
QT_MOC_LITERAL(3, 29, 15), // "boatSideChanged"
QT_MOC_LITERAL(4, 45, 8), // "QPoint**"
QT_MOC_LITERAL(5, 54, 16), // "boatSideChanged2"
QT_MOC_LITERAL(6, 71, 11), // "setLeftBoat"
QT_MOC_LITERAL(7, 83, 12), // "setRightBoat"
QT_MOC_LITERAL(8, 96, 12), // "setLeftBoat2"
QT_MOC_LITERAL(9, 109, 13), // "setRightBoat2"
QT_MOC_LITERAL(10, 123, 11), // "setCritLine"
QT_MOC_LITERAL(11, 135, 14), // "changeCritLine"
QT_MOC_LITERAL(12, 150, 14), // "missionChanged"
QT_MOC_LITERAL(13, 165, 9) // "curr_miss"

    },
    "CameraPanel\0critLineChanged\0\0"
    "boatSideChanged\0QPoint**\0boatSideChanged2\0"
    "setLeftBoat\0setRightBoat\0setLeftBoat2\0"
    "setRightBoat2\0setCritLine\0changeCritLine\0"
    "missionChanged\0curr_miss"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_CameraPanel[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
      10,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       3,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    2,   64,    2, 0x06 /* Public */,
       3,    1,   69,    2, 0x06 /* Public */,
       5,    1,   72,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       6,    0,   75,    2, 0x0a /* Public */,
       7,    0,   76,    2, 0x0a /* Public */,
       8,    0,   77,    2, 0x0a /* Public */,
       9,    0,   78,    2, 0x0a /* Public */,
      10,    0,   79,    2, 0x0a /* Public */,
      11,    2,   80,    2, 0x0a /* Public */,
      12,    1,   85,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void, QMetaType::Int, QMetaType::Int,    2,    2,
    QMetaType::Void, 0x80000000 | 4,    2,
    QMetaType::Void, 0x80000000 | 4,    2,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int, QMetaType::Int,    2,    2,
    QMetaType::Void, QMetaType::Int,   13,

       0        // eod
};

void CameraPanel::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<CameraPanel *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->critLineChanged((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2]))); break;
        case 1: _t->boatSideChanged((*reinterpret_cast< QPoint**(*)>(_a[1]))); break;
        case 2: _t->boatSideChanged2((*reinterpret_cast< QPoint**(*)>(_a[1]))); break;
        case 3: _t->setLeftBoat(); break;
        case 4: _t->setRightBoat(); break;
        case 5: _t->setLeftBoat2(); break;
        case 6: _t->setRightBoat2(); break;
        case 7: _t->setCritLine(); break;
        case 8: _t->changeCritLine((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2]))); break;
        case 9: _t->missionChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (CameraPanel::*)(int , int );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CameraPanel::critLineChanged)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (CameraPanel::*)(QPoint * * );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CameraPanel::boatSideChanged)) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (CameraPanel::*)(QPoint * * );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&CameraPanel::boatSideChanged2)) {
                *result = 2;
                return;
            }
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject CameraPanel::staticMetaObject = { {
    &rviz::Panel::staticMetaObject,
    qt_meta_stringdata_CameraPanel.data,
    qt_meta_data_CameraPanel,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *CameraPanel::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *CameraPanel::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_CameraPanel.stringdata0))
        return static_cast<void*>(this);
    return rviz::Panel::qt_metacast(_clname);
}

int CameraPanel::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = rviz::Panel::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 10)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 10;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 10)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 10;
    }
    return _id;
}

// SIGNAL 0
void CameraPanel::critLineChanged(int _t1, int _t2)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)), const_cast<void*>(reinterpret_cast<const void*>(&_t2)) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}

// SIGNAL 1
void CameraPanel::boatSideChanged(QPoint * * _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 1, _a);
}

// SIGNAL 2
void CameraPanel::boatSideChanged2(QPoint * * _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
