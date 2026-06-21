#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACNX2EMU 0.1 - Switch 2 Leak Edition
Real ARM64-style Opcodes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

BG = "#0f0f17"
PANEL = "#1f1f2e"
ACCENT = "#00d4ff"
TEXT = "#e0f0ff"

class ACNX2Assembler:
    def assemble(self, source: str) -> bytes:
        program = bytearray()
        for line in source.splitlines():
            line = line.strip().split(';')[0].strip()
            if not line: continue
            parts = line.replace(',', ' ').split()
            mnem = parts[0].upper()

            if mnem == "NOP": program += bytes([0x00, 0, 0, 0])
            elif mnem == "MOV": program += bytes([0x01, int(parts[1][1:])&0xF, 0, int(parts[2])&0xFF])
            elif mnem == "ADD": program += bytes([0x02, int(parts[1][1:])&0xF, 0, int(parts[2])&0xFF])
            elif mnem == "SUB": program += bytes([0x03, int(parts[1][1:])&0xF, 0, int(parts[2])&0xFF])
            elif mnem == "LDR": program += bytes([0x04, 0, 0, 0])   # Load Register
            elif mnem == "STR": program += bytes([0x05, 0, 0, 0])   # Store Register
            elif mnem == "B": program += bytes([0x06, 0, 0, 0])     # Branch
            elif mnem == "BL": program += bytes([0x07, 0, 0, 0])    # Branch with Link
            elif mnem == "CMP": program += bytes([0x08, 0, 0, 0])   # Compare
            elif mnem == "RECT": program += bytes([0x10, int(parts[1][1:])&0xF, int(parts[2][1:])&0xF, int(parts[3])&0xFF])
            elif mnem == "JOYCON": program += bytes([0x20, 0, 0, 0])
            elif mnem == "DOCK": program += bytes([0x30, 0, 0, 0])
            elif mnem == "HALT": program += bytes([0xFF, 0, 0, 0])
        return bytes(program)


class ACNX2VM:
    def __init__(self):
        self.x = 100
        self.y = 50
        self.halted = False
        self.program = b""
        self.pc = 0
        self.mode = "HANDHELD"

    def load(self, bytecode: bytes):
        self.program = bytecode
        self.pc = 0
        self.halted = False

    def step(self):
        if self.halted or not self.program or self.pc >= len(self.program):
            self.halted = True
            return
        opcode = self.program[self.pc]
        self.pc += 4

        if opcode == 0x01: self.x = self.program[self.pc-1] * 2
        elif opcode == 0x02: self.x = (self.x + self.program[self.pc-1]) % 290
        elif opcode == 0x03: self.x = max(0, self.x - self.program[self.pc-1])
        elif opcode == 0x10: self.x = self.program[self.pc-3] * 20; self.y = self.program[self.pc-2] * 20
        elif opcode == 0x20: self.x += 12
        elif opcode == 0x30: self.mode = "DOCK"
        elif opcode == 0xFF: self.halted = True

    def draw(self, canvas, scale=3):
        canvas.delete("all")
        s = scale
        w, h = 320*s, 180*s
        canvas.create_rectangle(0, 0, w, h, fill="#000000")

        if self.mode == "DOCK":
            canvas.create_rectangle(25, 12, w-25, h-12, outline="#ffffff", width=22)
            canvas.create_text(w//2, 38, text="SWITCH 2 DOCK MODE", fill=ACCENT, font=("Consolas", 17, "bold"))

        canvas.create_rectangle(self.x*s, self.y*s, (self.x+58)*s, (self.y+50)*s, fill=ACCENT, outline="#ffffff", width=6)


class ACNX2EMU:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ACNX2EMU 0.1 - Switch 2 (ARM64 Leak)")
        self.root.configure(bg=BG)
        self.root.geometry("1420x880")

        self.vm = ACNX2VM()
        self.assembler = ACNX2Assembler()
        self.running = False

        self._build_ui()
        self._frame_loop()

    def _build_ui(self):
        top = tk.Frame(self.root, bg="#003087", height=60)
        top.pack(fill="x")
        tk.Label(top, text="ACNX2EMU 0.1", bg="#003087", fg="white", font=("Consolas", 18, "bold")).pack(side="left", padx=25, pady=12)

        tb = tk.Frame(self.root, bg=PANEL, height=60)
        tb.pack(fill="x", padx=12, pady=10)

        ttk.Button(tb, text="▶ Run", command=self.toggle_run).pack(side="left", padx=6)
        ttk.Button(tb, text="⏹ Stop", command=self.stop).pack(side="left", padx=6)
        ttk.Button(tb, text="Step", command=self.step).pack(side="left", padx=6)
        ttk.Button(tb, text="Load .nx2", command=self.load).pack(side="left", padx=6)
        ttk.Button(tb, text="Assemble", command=self.assemble).pack(side="left", padx=6)
        ttk.Button(tb, text="Mode", command=self.toggle_mode).pack(side="left", padx=6)

        main = tk.PanedWindow(self.root, orient="horizontal", bg=BG)
        main.pack(fill="both", expand=True, padx=12, pady=5)

        left = tk.Frame(main, bg=PANEL)
        main.add(left, width=580)
        tk.Label(left, text="Code Editor (ARM64 Style)", bg=PANEL, fg=ACCENT, font=("Consolas", 14, "bold")).pack(anchor="w", padx=15, pady=10)
        self.editor = scrolledtext.ScrolledText(left, bg="#1a1a2e", fg=TEXT, font=("Consolas", 11))
        self.editor.pack(fill="both", expand=True, padx=15, pady=5)
        self.editor.insert("1.0", """; Switch 2 ARM64 Example
MOV R0, 110
MOV R1, 65
RECT R0, R1, 50
JOYCON
DOCK
HALT
""")

        right = tk.Frame(main, bg=BG)
        main.add(right, stretch="always")
        tk.Label(right, text="Switch 2 Screen", bg=BG, fg=ACCENT, font=("Consolas", 14, "bold")).pack(anchor="w", padx=15, pady=10)
        self.canvas = tk.Canvas(right, width=960, height=540, bg="#000000", highlightthickness=18, highlightbackground="#ffffff")
        self.canvas.pack(pady=15)

        self.status = tk.Label(self.root, text="ACNX2EMU 0.1 - Switch 2 Leak Ready", bg=PANEL, fg=TEXT, anchor="w", padx=20)
        self.status.pack(fill="x", side="bottom")

    def load(self):
        path = filedialog.askopenfilename(filetypes=[("NX2", "*.nx2 *.txt")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", code)
            self.assemble()

    def assemble(self):
        code = self.editor.get("1.0", "end").strip()
        try:
            bytecode = self.assembler.assemble(code)
            self.vm.load(bytecode)
            self.status.config(text=f"Assembled {len(bytecode)} bytes")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_run(self):
        self.running = not self.running
        self.status.config(text="RUNNING..." if self.running else "PAUSED")

    def stop(self):
        self.running = False
        self.status.config(text="Stopped")

    def step(self):
        self.vm.step()
        self.render()

    def toggle_mode(self):
        self.vm.mode = "DOCK" if self.vm.mode == "HANDHELD" else "HANDHELD"
        self.render()

    def render(self):
        self.vm.draw(self.canvas, scale=3)

    def _frame_loop(self):
        if self.running:
            for _ in range(10):
                self.vm.step()
            self.render()
        self.root.after(16, self._frame_loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ACNX2EMU().run()
