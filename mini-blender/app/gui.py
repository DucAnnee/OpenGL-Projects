# type: ignore
# pyright: ignore-all
# ruff: noqa

import os
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
import numpy as np
import OpenGL.GL as GL
from tkinter import Tk, filedialog

from app.object_factory import OBJECT_FACTORY, OBJECT_CATEGORIES


class GUI:
    def __init__(self, window):
        imgui.create_context()
        self.impl = GlfwRenderer(window, attach_callbacks=False)
        self.show_scene_panel = True
        self.show_info_panel = True
        self.equation_input = ""
        self.show_equation_input = False
        self.error_msg = ""

    def begin_frame(self):
        self.impl.process_inputs()
        imgui.new_frame()

    def end_frame(self):
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def render_menu_bar(self, viewer):
        # fmt: off
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, _ = imgui.menu_item("Quit", "Esc/Ctrl+Q")
                if clicked_quit:
                    glfw.set_window_should_close(viewer.win, True)
                imgui.end_menu()

            if imgui.begin_menu("View", True):
                _, self.show_scene_panel = imgui.menu_item("Object List Panel", None, self.show_scene_panel)
                _, self.show_info_panel = imgui.menu_item("Infomation Panel", None, self.show_info_panel)
                _, viewer.display_grid = imgui.menu_item("World grid", None, viewer.display_grid)
                imgui.end_menu()

            if imgui.begin_menu("Rendering", True):
                if imgui.menu_item("Wireframe", "Ctrl+W", viewer.rendering_mode == "wireframe")[0]:
                    viewer.rendering_mode = "wireframe"
                if imgui.menu_item("Flat", "Ctrl+F", viewer.rendering_mode == "flat")[0]:
                    viewer.rendering_mode = "flat"
                if imgui.menu_item("Gouraud", "Ctrl+G", viewer.rendering_mode == "gouraud")[0]:
                    viewer.rendering_mode = "gouraud"
                if imgui.menu_item("Phong", "Ctrl+P", viewer.rendering_mode == "phong")[0]:
                    viewer.rendering_mode = "phong"
                if imgui.menu_item("Texture", "Ctrl+T", viewer.rendering_mode == "texture")[0]:
                    viewer.rendering_mode = "texture"
                imgui.end_menu()

            imgui.end_main_menu_bar()

    def render_info_panel(self, viewer):
        if not self.show_info_panel:
            return

        window_width, window_height = glfw.get_window_size(self.impl.window)

        panel_width = 0.3 * window_width
        imgui.set_next_window_position(0, 20)
        imgui.set_next_window_size(panel_width, -1)

        flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE

        expanded, opened = imgui.begin("Infomation", True, 0)
        if expanded:
            imgui.text("LMB Drag: Rotate")
            imgui.text("Shift+LMB/RMB Drag: Pan")
            imgui.text("Mouse Scroll: Zoom In/Out")
            imgui.text("M: Switch manipulation mode")
            imgui.text("Tab: Select next object")
            imgui.text("Shift+Tab: Select previous object")
            imgui.text("Delete: Delete selected object")
            imgui.separator()
            if viewer.manipulation_mode == "camera":
                imgui.text("Current Mode: Camera")
            else:
                imgui.text("Current Mode: Object")
            if (
                viewer.manipulation_mode == "object"
                and viewer.scene.selected_index is not None
            ):
                imgui.text("Arrow Keys: Move on XZ plane")
                imgui.text("E/Q: Move up/down")
                imgui.text("LMB Drag: Rotate")
                imgui.text("0: Reset object transformation")

        imgui.end()

    def render_scene_panel(self, scene_manager):
        if not self.show_scene_panel:
            return

        window_width, window_height = glfw.get_window_size(self.impl.window)

        panel_width = 0.2 * window_width
        imgui.set_next_window_position(window_width - panel_width, 20)
        imgui.set_next_window_size(panel_width, window_height - 20)
        flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE

        expanded, opened = imgui.begin("Object list", True, flags)
        if expanded:
            for idx, obj in enumerate(scene_manager.objects):
                is_selected = idx == scene_manager.selected_index

                label = f"{obj.name}"

                if imgui.selectable(f"{label}###{idx}", is_selected)[0]:
                    scene_manager.selected_index = idx

                # right-click context menu
                if imgui.begin_popup_context_item(f"context_{idx}"):
                    imgui.text(f"'{obj.name}'")
                    imgui.separator()
                    if imgui.selectable("Delete")[0]:
                        scene_manager.remove(idx)
                    imgui.end_popup()

            imgui.separator()

            # Add object button with dropdown
            if imgui.button("Add Object", width=-1):
                imgui.open_popup("add_object_popup")

            if imgui.begin_popup("add_object_popup"):
                for category, objects in OBJECT_CATEGORIES.items():
                    if imgui.tree_node(
                        f"{category} Objects", imgui.TREE_NODE_DEFAULT_OPEN
                    ):
                        for obj_name in objects:
                            if imgui.selectable(obj_name)[0]:
                                new_obj = OBJECT_FACTORY[obj_name]()
                                scene_manager.add(new_obj)
                                print(f"Added object: {obj_name}")
                        imgui.tree_pop()
                    imgui.separator()

                if imgui.selectable("Custom Equation")[0]:
                    self.show_equation_input = True
                    imgui.close_current_popup()

                imgui.separator()

                if imgui.selectable("Custom Model (.obj, .ply)")[0]:
                    file_path = self.open_native_file_dialog()
                    if file_path:
                        try:
                            from objects.custom import CustomModel

                            model = CustomModel(model_path=file_path).setup()
                            file_name = os.path.basename(file_path)
                            scene_manager.add(model, name=file_name)
                            print(f"Loaded model: {file_name}")
                        except Exception as e:
                            print(f"Error loading model: {e}")
                            self.equation_error = f"Failed to load model: {str(e)}"

                imgui.end_popup()

        if self.show_equation_input:
            imgui.open_popup("Equation Input")
            self.show_equation_input = False

        if imgui.begin_popup_modal("Equation Input", True)[0]:
            imgui.text("Enter equation in terms of x and y:")
            imgui.text("Example: sin(sqrt(x**2 + y**2))")
            imgui.spacing()

            # set focus
            if imgui.is_window_appearing():
                imgui.set_keyboard_focus_here()

            changed, self.equation_input = imgui.input_text(
                "##eq", self.equation_input, 256
            )

            # show error if any
            if self.error_msg:
                imgui.spacing()
                imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.3, 0.3, 1.0)
                imgui.text_wrapped(self.error_msg)
                imgui.pop_style_color()

            imgui.spacing()

            if imgui.button("Create", width=100):
                from objects.equation import Equation

                try:
                    eq = Equation(func=str(self.equation_input)).setup()
                    scene_manager.add(eq, name=f"Eq: {self.equation_input[:15]}")
                    imgui.close_current_popup()
                    self.equation_input = ""
                    self.error_msg = ""
                except (ValueError, Exception):
                    self.error_msg = "ERROR: The equatiton is invalid"

            imgui.same_line()
            if imgui.button("Cancel", width=100):
                self.error_msg = ""
                self.equation_input = ""
                imgui.close_current_popup()

            imgui.end_popup()

        imgui.end()

    def shutdown(self):
        self.impl.shutdown()

    @staticmethod
    def open_native_file_dialog(title="Select 3D File"):
        import platform
        import subprocess

        system = platform.system()

        if system == "Windows":
            # windows: use PowerShell with OpenFileDialog
            ps_script = (
                '''
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.OpenFileDialog
            $dialog.Title = "'''
                + title
                + """"
            $dialog.Filter = "All Files (*.*)|*.*|OBJ Files (*.obj)|*.obj|PLY Files (*.ply)|*.ply"
            $dialog.ShowDialog() | Out-Null
            $dialog.FileName
            """
            )
            result = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True
            )
            file_path = result.stdout.strip()
            return file_path if file_path else None

        elif system == "Darwin":  # macOS
            # macOS: Use osascript
            script = f"""
            tell application "System Events"
                activate
                set theFile to choose file with prompt "{title}"
                return POSIX path of theFile
            end tell
            """
            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True
            )
            file_path = result.stdout.strip()
            return file_path if file_path else None

        elif system == "Linux":
            # try kdialog
            try:
                result = subprocess.run(
                    [
                        "kdialog",
                        "--getopenfilename",
                        "~",
                        "*.obj *.gltf *.glb|3D Models\n*|All Files",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                file_path = result.stdout.strip()
                return file_path if file_path else None
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            # try zenity
            try:
                result = subprocess.run(
                    [
                        "zenity",
                        "--file-selection",
                        "--title=" + title,
                        "--file-filter=3D Models (obj,ply) | *.obj *.ply",
                        "--file-filter=All files | *",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                file_path = result.stdout.strip()
                return file_path if file_path else None
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

            # fallback
            print("No native dialog found, falling back to tkinter")
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(title=title)
            root.destroy()
            return file_path if file_path else None

        return None
