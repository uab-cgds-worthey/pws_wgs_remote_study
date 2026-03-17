def hex_to_plotly_rgba(hex_color, alpha=1.0):
    """
    Converts a hexadecimal color string (e.g., "#RRGGBB" or "RRGGBB")
    to an RGBA string for Plotyl in the form of 'rgba(R, G, B, A)'.
    """
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]  # Remove '#' if present

    if len(hex_color) != 6:
        raise ValueError(
            "Hexadecimal color string must be 6 characters long (excluding '#')."
        )
    if alpha > 1 or alpha < 0:
        raise ValueError("Alpha must be a decimal value of 0 to 1")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return f"rgba({r}, {g}, {b}, {alpha})"


class CohortColorPallet:
    """Reusable color scheme for consistent colors used across figures"""

    def __init__(self) -> None:
        # record colorblidness aware color scheme
        # from https://doi.org/10.5281/zenodo.3381072
        self.color_pallet = {
            "salmon": "#EE6677",
            "green": "#228833",
            "dark blue": "#4477AA",
            "yellow": "#CCBB44",
            "light blue": "#66CCEE",
            "magenta": "#AA3377",
            "gray": "#BBBBBB",
            "orange": "#f8961e",
            "black": "#000000",
        }

        # define the color used for each MDx category
        self.colors_by_cat = {
            "Type I & 15q26": "yellow",
            "Type I": "yellow",
            "Classic Type I": "yellow",
            "Complex Type I": "yellow",
            "Type II": "green",
            "Classic Type II": "green",
            "Complex Type II": "green",
            "UPD": "dark blue",
            "UPD/ICD": "dark blue",
            "Isodisomy": "dark blue",
            "Segmental Isodisomy": "dark blue",
            "Heterodisomy or Epimutation": "dark blue",
            "Epimutation": "dark blue",
            "Mosaic Epimutation": "dark blue",
            "Atypical UPD": "dark blue",
            "ICD & Atypical": "salmon",
            "Atypical deletion": "salmon",
            "Atypical deletion*": "salmon",
            "Deletion & Translocation": "salmon",
            "Deletion*": "salmon",
            "Deletion": "orange",
            "Deletion (Unspecified)": "light blue",
            "IC deletion": "gray",
            "Unknown": "gray",
        }

    def getCategoryColorPalletHex(self) -> dict:
        return {cat: self.getCategoryColorHex(cat) for cat in self.colors_by_cat}

    def getCategoryColor(self, category: str) -> str:
        return self.colors_by_cat.get(category, "black")

    def getCategoryColorHex(self, category: str) -> str:
        return self.color_pallet.get(
            self.getCategoryColor(category), self.color_pallet["black"]
        )

    def getCategoryColorRGBA(self, category: str, alpha=1.0) -> str:
        return hex_to_plotly_rgba(self.getCategoryColorHex(category), alpha)

    def getPalletColorHex(self, color: str) -> str:
        if color not in self.color_pallet:
            raise RuntimeError(f"Color {color} not in cohort pallet.")
        return self.color_pallet[color]

    def getPalletColorRGBA(self, color: str, alpha=1.0) -> str:
        return hex_to_plotly_rgba(self.getPalletColorHex(color), alpha)
