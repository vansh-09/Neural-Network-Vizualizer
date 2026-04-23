from __future__ import annotations

import argparse
import random
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import messagebox
from typing import Iterable


DEFAULT_LAYERS = [3, 5, 4, 2]
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 780
CANVAS_BACKGROUND = "#0f172a"
PANEL_BACKGROUND = "#111827"
TEXT_COLOR = "#e5e7eb"
ACCENT_COLOR = "#38bdf8"
NODE_BASE_COLOR = "#1f2937"
POSITIVE_COLOR = "#60a5fa"
NEGATIVE_COLOR = "#f87171"
EDGE_NEUTRAL_COLOR = "#94a3b8"


@dataclass
class NetworkState:
    layers: list[int]
    activations: list[list[float]] = field(default_factory=list)
    weights: list[list[list[float]]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.activations:
            self.activations = [self._random_values(count, 0.15, 0.95) for count in self.layers]
        if not self.weights:
            self.weights = [
                [self._random_values(previous_count, -1.0, 1.0) for _ in range(next_count)]
                for previous_count, next_count in zip(self.layers[:-1], self.layers[1:], strict=True)
            ]

    @staticmethod
    def _random_values(count: int, lower: float, upper: float) -> list[float]:
        return [random.uniform(lower, upper) for _ in range(count)]

    def randomize_activations(self) -> None:
        self.activations = [self._random_values(count, 0.15, 0.95) for count in self.layers]

    def randomize_weights(self) -> None:
        self.weights = [
            [self._random_values(previous_count, -1.0, 1.0) for _ in range(next_count)]
            for previous_count, next_count in zip(self.layers[:-1], self.layers[1:], strict=True)
        ]


def parse_layers(raw_value: str) -> list[int]:
    cleaned = raw_value.replace("x", ",").replace(" ", "")
    parts = [part for part in cleaned.split(",") if part]
    if len(parts) < 2:
        raise ValueError("Enter at least two layers, for example 3,5,4,2")

    layers = [int(part) for part in parts]
    if any(layer < 1 for layer in layers):
        raise ValueError("Layer sizes must be positive integers")
    return layers


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def interpolate_channel(start: int, end: int, amount: float) -> int:
    return round(start + (end - start) * amount)


def activation_to_color(value: float) -> str:
    normalized = clamp(value, 0.0, 1.0)
    red = interpolate_channel(31, 34, 1.0 - normalized)
    green = interpolate_channel(41, 197, normalized)
    blue = interpolate_channel(55, 94, normalized)
    return f"#{red:02x}{green:02x}{blue:02x}"


def weight_to_color(weight: float) -> str:
    magnitude = clamp(abs(weight), 0.0, 1.0)
    if weight >= 0:
        return f"#{interpolate_channel(148, 96, magnitude):02x}{interpolate_channel(163, 165, magnitude):02x}{interpolate_channel(184, 250, magnitude):02x}"
    return f"#{interpolate_channel(148, 248, magnitude):02x}{interpolate_channel(163, 113, magnitude):02x}{interpolate_channel(184, 113, magnitude):02x}"


class NeuralNetworkVisualizer(tk.Tk):
    def __init__(self, layers: list[int]) -> None:
        super().__init__()
        self.title("Neural Network Visualizer")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1024, 680)
        self.configure(bg=PANEL_BACKGROUND)

        self.state = NetworkState(layers=layers)
        self.node_positions: list[list[tuple[float, float]]] = []
        self.layer_entry = tk.StringVar(value=", ".join(str(layer) for layer in layers))
        self.status_text = tk.StringVar(value="Ready")

        self._build_ui()
        self._render()

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self, bg=PANEL_BACKGROUND, padx=16, pady=12)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        title_block = tk.Frame(toolbar, bg=PANEL_BACKGROUND)
        title_block.pack(side=tk.LEFT, anchor=tk.W)

        title = tk.Label(
            title_block,
            text="Neural Network Visualizer",
            bg=PANEL_BACKGROUND,
            fg=TEXT_COLOR,
            font=("Helvetica", 18, "bold"),
        )
        title.pack(anchor=tk.W)

        subtitle = tk.Label(
            title_block,
            text="Layer colors represent activations. Connection color and thickness represent weight sign and magnitude.",
            bg=PANEL_BACKGROUND,
            fg="#94a3b8",
            font=("Helvetica", 10),
        )
        subtitle.pack(anchor=tk.W, pady=(3, 0))

        controls = tk.Frame(toolbar, bg=PANEL_BACKGROUND)
        controls.pack(side=tk.RIGHT, anchor=tk.E)

        tk.Label(controls, text="Layers", bg=PANEL_BACKGROUND, fg=TEXT_COLOR, font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        layer_entry = tk.Entry(controls, textvariable=self.layer_entry, width=22, bg="#1f2937", fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief=tk.FLAT)
        layer_entry.grid(row=1, column=0, padx=(0, 8), pady=(3, 0))

        tk.Button(controls, text="Apply", command=self.apply_layers, bg=ACCENT_COLOR, fg="#0f172a", activebackground="#7dd3fc", relief=tk.FLAT, padx=14, pady=4).grid(row=1, column=1, pady=(3, 0), padx=(0, 8))
        tk.Button(controls, text="Randomize activations", command=self.randomize_activations, bg="#334155", fg=TEXT_COLOR, activebackground="#475569", relief=tk.FLAT, padx=14, pady=4).grid(row=1, column=2, pady=(3, 0), padx=(0, 8))
        tk.Button(controls, text="Randomize weights", command=self.randomize_weights, bg="#334155", fg=TEXT_COLOR, activebackground="#475569", relief=tk.FLAT, padx=14, pady=4).grid(row=1, column=3, pady=(3, 0))

        self.canvas = tk.Canvas(self, bg=CANVAS_BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _event: self._render())

        footer = tk.Frame(self, bg=PANEL_BACKGROUND, padx=16, pady=10)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(footer, textvariable=self.status_text, bg=PANEL_BACKGROUND, fg="#cbd5e1", font=("Helvetica", 10)).pack(anchor=tk.W)

    def apply_layers(self) -> None:
        try:
            layers = parse_layers(self.layer_entry.get())
        except ValueError as error:
            messagebox.showerror("Invalid layers", str(error))
            return

        self.state = NetworkState(layers=layers)
        self.status_text.set(f"Applied architecture: {' -> '.join(str(layer) for layer in layers)}")
        self._render()

    def randomize_activations(self) -> None:
        self.state.randomize_activations()
        self.status_text.set("Randomized activations")
        self._render()

    def randomize_weights(self) -> None:
        self.state.randomize_weights()
        self.status_text.set("Randomized weights")
        self._render()

    def _render(self) -> None:
        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        margin_x = 90
        margin_y = 55
        available_width = max(width - 2 * margin_x, 1)
        available_height = max(height - 2 * margin_y, 1)

        self._draw_grid(width, height)
        self.node_positions = self._compute_positions(margin_x, margin_y, available_width, available_height)
        self._draw_connections()
        self._draw_nodes()
        self._draw_header(width)

    def _draw_grid(self, width: int, height: int) -> None:
        grid_color = "#172033"
        for x in range(0, width, 48):
            self.canvas.create_line(x, 0, x, height, fill=grid_color)
        for y in range(0, height, 48):
            self.canvas.create_line(0, y, width, y, fill=grid_color)

    def _compute_positions(
        self,
        margin_x: float,
        margin_y: float,
        available_width: float,
        available_height: float,
    ) -> list[list[tuple[float, float]]]:
        layers = len(self.state.layers)
        x_spacing = available_width / max(layers - 1, 1)
        positions: list[list[tuple[float, float]]] = []

        for layer_index, neuron_count in enumerate(self.state.layers):
            layer_x = margin_x + layer_index * x_spacing
            if neuron_count == 1:
                y_values = [margin_y + available_height / 2]
            else:
                y_spacing = available_height / (neuron_count - 1)
                y_values = [margin_y + neuron_index * y_spacing for neuron_index in range(neuron_count)]
            positions.append([(layer_x, y_value) for y_value in y_values])
        return positions

    def _draw_connections(self) -> None:
        for layer_index in range(len(self.node_positions) - 1):
            source_nodes = self.node_positions[layer_index]
            target_nodes = self.node_positions[layer_index + 1]
            weights = self.state.weights[layer_index]
            for target_index, target_position in enumerate(target_nodes):
                for source_index, source_position in enumerate(source_nodes):
                    weight = weights[target_index][source_index]
                    line_width = 1 + abs(weight) * 4
                    self.canvas.create_line(
                        source_position[0] + 24,
                        source_position[1],
                        target_position[0] - 24,
                        target_position[1],
                        fill=weight_to_color(weight),
                        width=line_width,
                    )

    def _draw_nodes(self) -> None:
        for layer_index, layer_nodes in enumerate(self.node_positions):
            activations = self.state.activations[layer_index]
            for neuron_index, (x_position, y_position) in enumerate(layer_nodes):
                activation = activations[neuron_index]
                fill_color = activation_to_color(activation)
                radius = 24
                self.canvas.create_oval(
                    x_position - radius,
                    y_position - radius,
                    x_position + radius,
                    y_position + radius,
                    fill=fill_color,
                    outline="#e2e8f0",
                    width=2,
                )
                self.canvas.create_text(
                    x_position,
                    y_position,
                    text=f"{activation:.2f}",
                    fill="#f8fafc",
                    font=("Helvetica", 9, "bold"),
                )
            self.canvas.create_text(
                layer_nodes[0][0],
                24,
                text=f"Layer {layer_index + 1}\n({self.state.layers[layer_index]})",
                fill=TEXT_COLOR,
                font=("Helvetica", 10, "bold"),
                justify=tk.CENTER,
            )

    def _draw_header(self, width: int) -> None:
        architecture = "  →  ".join(str(layer) for layer in self.state.layers)
        self.canvas.create_text(
            width / 2,
            24,
            text=architecture,
            fill="#cbd5e1",
            font=("Helvetica", 13, "bold"),
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interactive neural network visualizer")
    parser.add_argument(
        "layers",
        nargs="?",
        default=",".join(str(layer) for layer in DEFAULT_LAYERS),
        help="Layer sizes, for example 3,5,4,2 or 3x5x4x2",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_argument_parser()
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    try:
        layers = parse_layers(arguments.layers)
    except ValueError as error:
        parser.error(str(error))
        return

    app = NeuralNetworkVisualizer(layers)
    app.mainloop()


if __name__ == "__main__":
    main()
