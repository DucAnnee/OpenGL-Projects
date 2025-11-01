# type: ignore

import imgui
from imgui.integrations.glfw import GlfwRenderer
from objects.molecule import Molecule
from app.object_factory import ATOM_FACTORY, MOLECULE_FACTORY, MOLECULE_DICT, ATOM_DICT
from lib.molecule_recipes import recipes
import glfw


class GUI:
    def __init__(self, window):
        imgui.create_context()
        self.impl = GlfwRenderer(window, attach_callbacks=False)
        self.show_selection_panel = True
        self.show_periodic_table = False
        self.show_atom_info = True

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
                if viewer.rendering_mode == "molecule":
                    _, self.show_selection_panel = imgui.menu_item("Molecule Selection Panel", None, self.show_selection_panel)
                else:
                    _, self.show_atom_info = imgui.menu_item("Atom Info Pnael", None, self.show_atom_info)
                    _, self.show_periodic_table = imgui.menu_item("Periodic Table Selection", None, self.show_periodic_table)
                imgui.end_menu()

            if imgui.begin_menu("Mode", True):
                if imgui.menu_item("Atom", "Ctrl+A", viewer.rendering_mode == "atom")[0]:
                    viewer.rendering_mode = "atom"
                if imgui.menu_item("Molecule", "Ctrl+M", viewer.rendering_mode == "molecule")[0]:
                    viewer.rendering_mode = "molecule"
                imgui.end_menu()

            imgui.end_main_menu_bar()

    def render_molecule_panel(self, viewer):
        if not self.show_selection_panel:
            return

        window_width, window_height = glfw.get_window_size(self.impl.window)

        panel_width = 0.3 * window_width
        imgui.set_next_window_position(window_width - panel_width, 20)
        imgui.set_next_window_size(panel_width, -1)

        flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE

        if viewer.rendering_mode == "molecule":
            if imgui.begin("Molecule Selection Panel", True, flags):
                is_selected = viewer.scene.get_current_molecule_name()
                for molecule_name, recipe in recipes.items():
                    if imgui.selectable(molecule_name, molecule_name == is_selected)[0]:
                        if is_selected == molecule_name:
                            continue
                        obj = Molecule.build_from_recipe(recipe)
                        viewer.scene.set_current_molecule(obj)
                        viewer.scene.set_current_molecule_name(molecule_name)
            imgui.end()

    def render_periodic_table(self, viewer):
        # fmt: off
        if not self.show_periodic_table:
            return

        window_width, window_height = glfw.get_window_size(self.impl.window)
        panel_width = 0.8 * window_width
        panel_height = 0.7 * window_height
        imgui.set_next_window_position((window_width - panel_width) / 2, (window_height - panel_height) / 2)
        imgui.set_next_window_size(panel_width, panel_height)

        flags = imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE

        button_size = 30
        spacing = 5

        if imgui.begin("Periodic Table", True, flags):
            start_pos = imgui.get_cursor_screen_pos()

            for period, atoms in ATOM_FACTORY.items():
                for name, (obj, group) in atoms.items():
                    # Calculate position
                    x = start_pos[0] + (group - 1) * (button_size + spacing)
                    y = start_pos[1] + (period - 1) * (button_size + spacing)

                    imgui.set_cursor_screen_pos((x, y))

                    if imgui.button(name, button_size, button_size):
                        viewer.scene.set_current_atom(obj().setup())
                        self.show_periodic_table = False  # close after selection

            imgui.set_cursor_pos((panel_width / 2, panel_height - 20))
            if imgui.button("Close", 80, 30):
                self.show_periodic_table = False

            imgui.end()
        else:
            self.show_periodic_table = False

    def render_atom_info(self, viewer):
        if self.show_periodic_table or not self.show_atom_info:
            return
        symbol = viewer.scene.get_current_atom_name()
        info = ATOM_DICT[symbol]

        window_width, _ = glfw.get_window_size(self.impl.window)
        panel_width = 0.3 * window_width
        imgui.set_next_window_position(window_width - panel_width, 20)
        imgui.set_next_window_size(panel_width, -1)

        flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE

        if imgui.begin("Information", False, flags):
            imgui.text(f"Atomic Number: {info['atomic_number']}")
            imgui.same_line(panel_width - 100)
            imgui.text(f"Mass: {info['mass']:.3f}")

            imgui.spacing()
            imgui.spacing()

            imgui.set_cursor_pos_x((panel_width - imgui.calc_text_size(symbol)[0]) / 2)
            imgui.set_window_font_scale(2.0)
            imgui.text(symbol)
            imgui.set_window_font_scale(1.0)
            imgui.set_cursor_pos_x(
                (panel_width - imgui.calc_text_size(info["name"])[0]) / 2
            )
            imgui.text(info["name"])

            imgui.spacing()
            imgui.spacing()

            # Bottom row: Period/Group (left) and Category (right)
            imgui.text(f"P:{info['period']} G:{info['group']}")
            imgui.same_line(
                panel_width - imgui.calc_text_size(info["category"])[0] - 10
            )
            imgui.text(info["category"])

            if imgui.button("Select element", panel_width - 20, 30):
                self.show_periodic_table = True

            imgui.end()
