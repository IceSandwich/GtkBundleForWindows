# Gtk Bundle For Windows

## What is this?
This repository provides an easy way to setup gtk/gtkmm developmental environment on Windows since the official gtk bundle project doesn't maintained anymore.

All files are built under Windows 10 and Visual Studio 2017 with vcpkg.

And then use `gtkbundle.py` to extract and zip them.

## How to use?
Go to release tab and download whatever version you want.

Extract them somewhere else and use in Visual Studio.

**Remeber to add `<GtkBundleRoot>\bin` to your environment path.**

Currently provided:
- gtkmm 4.4.0  (contain gtk)    x64-windows
- ~~ gtkmm 3.22.2 (contain gtk)    x64-windows~~ (failed to bundle)
- gtk   4.4.0                   x86-windows

## Can't find specify version?
This repository can't update in time.

**You can make a bundle yourself!!!**

Follow these [steps](doc/makebundle.md).

## Test environment
**All packages doesn't fully be tested.**

I have no x86 devices so i can't test x86 packages. Let me know if it works in x86. Thanks.

## Useful links

[Official gvsbuild project](https://github.com/wingtk/gvsbuild)

[Gtk runtime env](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)