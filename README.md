# ADB & Fastboot GUI Toolbox

Кроссплатформенная графическая оболочка (GUI) для Android Platform-Tools (Linux / Windows).

## Возможности
- Полная кроссплатформенность (Windows, Ubuntu, Debian, Arch, Fedora и др.).
- Автопоиск `adb` и `fastboot` в `PATH` или выбор локальной папки.
- **Управление перезагрузкой**: System, Recovery, Bootloader/Fastboot, Fastbootd, EDL, Sideload.
- **Быстрый сервис**:
  - Установка APK в один клик.
  - Sideload прошивок (.zip).
  - Создание скриншота устройства напрямую на ПК.
  - Push / Pull файлов.
- **Fastboot менеджер**:
  - Разблокировка и блокировка загрузчика (`flashing unlock`, `oem unlock`).
  - Прошивка разделов (`boot`, `recovery`, `system`, `vendor`, `vbmeta`, `userdata`).
  - Разовая загрузка образа (`fastboot boot image.img`).
- **Инфо-панель**: просмотр параметров экрана, батареи, характеристик устройства.
- **Интерактивный лог / кастомная консоль**: выполнение любых произвольных команд.

## Установка и запуск

### 1. Установка зависимостей
Убедитесь, что установлен Python 3.8+:

