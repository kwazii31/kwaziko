"""
Combined Pet Maker + Spawner
Run: python pet_tool.py
Requires: Pillow

This app contains two tabs:
- Maker: 32x32 pixel sprite editor with frames and export
- Spawner: view exported sprites and spawn draggable pet windows

Exported frames go to assets/<name>_0.png, <name>_1.png ...
"""
import os
import glob
import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import shutil
import subprocess
import sys
import tempfile
from tkinter import font as tkfont
import webbrowser

PIXEL = 32
DEFAULT_ZOOM = 12
SCALE = 4
PALETTE = [
    (0,0,0,0),(34,34,34,255),(85,85,85,255),(170,170,170,255),
    (255,255,255,255),(255,0,0,255),(255,128,0,255),(255,255,0,255),
    (0,255,0,255),(0,255,255,255),(0,128,255,255),(0,0,255,255),
    (128,0,255,255),(255,0,255,255),(200,100,150,255),(150,75,0,255)
]
DEFAULT_ASSET_DIR = 'assets'

def asset_glob_pattern(asset_dir):
    return os.path.join(asset_dir, '*.png')

# Apply a clean ttk theme and fonts for a modern look
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'pet_tool_settings.json')

def load_settings():
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            'theme': 'light',
            'default_pixel': 32,
            'default_zoom': DEFAULT_ZOOM,
            'accent': 'blue',
            'show_grid': True,
            'onion': False,
            'assets_dir': DEFAULT_ASSET_DIR,
            'scale': SCALE,
            'animation_speed': 120,
            'auto_refresh': True,
            'always_on_top': True,
            'start_minimized': False
        }

def save_settings(s):
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

def ensure_builtin_presets(asset_dir=DEFAULT_ASSET_DIR, pixel=PIXEL):
    try:
        preset_dir = os.path.join(asset_dir, 'presets')
        os.makedirs(preset_dir, exist_ok=True)

        def write_images(prefix, frames, behavior):
            for i, im in enumerate(frames):
                path = os.path.join(preset_dir, f'{prefix}_{i}.png')
                if not os.path.exists(path):
                    try:
                        im.save(path)
                    except Exception:
                        pass
            meta_path = os.path.join(preset_dir, f'{prefix}_meta.json')
            if not os.path.exists(meta_path):
                try:
                    with open(meta_path, 'w', encoding='utf-8') as mf:
                        json.dump({'behavior': behavior}, mf, indent=2)
                except Exception:
                    pass

        # simple blob preset (2 frames)
        try:
            frames = []
            im1 = Image.new('RGBA', (pixel, pixel), (0,0,0,0))
            d1 = ImageDraw.Draw(im1)
            d1.ellipse((6,6,pixel-6,pixel-6), fill=(200,80,200,255))
            frames.append(im1)
            im2 = Image.new('RGBA', (pixel, pixel), (0,0,0,0))
            d2 = ImageDraw.Draw(im2)
            d2.ellipse((6,8,pixel-6,pixel-4), fill=(200,80,200,255))
            frames.append(im2)
            write_images('blob', frames, {'mode': 'wander', 'speed': 3, 'animation_speed': 180})
        except Exception:
            pass

        # simple square preset (2 frames) - follows cursor
        try:
            frames = []
            im1 = Image.new('RGBA', (pixel, pixel), (0,0,0,0))
            d1 = ImageDraw.Draw(im1)
            d1.rectangle((6,6,pixel-6,pixel-6), fill=(80,180,200,255))
            frames.append(im1)
            im2 = Image.new('RGBA', (pixel, pixel), (0,0,0,0))
            d2 = ImageDraw.Draw(im2)
            d2.rectangle((6,6,pixel-6,pixel-6), fill=(60,160,200,255))
            frames.append(im2)
            write_images('square', frames, {'mode': 'follow', 'speed': 6, 'animation_speed': 100})
        except Exception:
            pass

    except Exception:
        pass

def apply_ui_theme(root=None, theme='light'):
    try:
        s = ttk.Style()
        # allow user-chosen accent from settings
        try:
            _settings_accent = load_settings().get('accent', 'blue')
        except Exception:
            _settings_accent = 'blue'
        accent_map = {
            'blue': '#2563eb',
            'teal': '#14b8a6',
            'purple': '#7c3aed',
            'orange': '#fb923c',
            'pink': '#ec4899'
        }
        accent = accent_map.get(_settings_accent, '#2563eb')
        # modernized light/dark palettes with subtle accents
        if theme == 'dark':
            s.theme_use('alt')
            bg = '#1f1f23'
            panel = '#252528'
            fg = '#e8e8e8'
        else:
            s.theme_use('clam')
            bg = '#f6f7fb'
            panel = '#ffffff'
            fg = '#1f2430'
        default_font = ('Segoe UI', 11)
        s.configure('.', font=default_font)
        # Buttons: flatter, subtle accent for primary actions
        s.configure('TButton', background=panel, foreground=fg, padding=6, relief='flat')
        s.configure('Accent.TButton', background=accent, foreground='white', padding=6)
        s.configure('TLabel', background=bg, foreground=fg)
        s.configure('TFrame', background=bg)
        s.configure('TMenubutton', background=panel)
        s.configure('TCheckbutton', background=bg, foreground=fg)
        s.configure('TRadiobutton', background=bg, foreground=fg)
        s.configure('TEntry', fieldbackground=panel, foreground=fg)
        s.configure('TNotebook', background=bg)
        s.configure('TNotebook.Tab', padding=[10, 6])
        s.configure('TNotebook.Tab', background=panel)
        # simple map for button hover/pressed visuals
        try:
            s.map('TButton', background=[('active', panel), ('pressed', panel)])
            s.map('Accent.TButton', background=[('active', accent), ('pressed', accent)])
        except Exception:
            pass
        if root:
            try:
                root.option_add('*Font', default_font)
                root.option_add('*background', bg)
                root.option_add('*foreground', fg)
                root.option_add('Listbox.background', panel)
                root.option_add('Listbox.foreground', fg)
                root.option_add('Entry.background', panel)
                root.option_add('Entry.foreground', fg)
                root.option_add('Text.background', panel)
                root.option_add('Button.activeBackground', panel)
                root.option_add('Canvas.background', panel)
                root.configure(bg=bg)
            except Exception:
                pass
    except Exception:
        pass

# ----------------- Maker Frame -----------------
class MakerFrame(tk.Frame):
    def __init__(self, master, assets_var: tk.StringVar, settings: dict = None):
        super().__init__(master)
        settings = settings or {}
        self._settings = settings
        # apply maker-specific preferences
        self._prefs = load_settings()
        self.zoom = int(settings.get('default_zoom', DEFAULT_ZOOM))
        self.current_color = PALETTE[5]
        # allow custom pixel size per-maker (default from module PIXEL or settings)
        self.pixel = int(settings.get('default_pixel', PIXEL))
        # animations: list of {'name': str, 'frames': [frame_arrays]}
        self.animations = [ {'name':'idle', 'frames':[self._new_frame()]} ]
        self.current_anim = 0
        self.current_frame = 0
        self.playing = False
        self.assets_var = assets_var
        self._build_ui()
        self._redraw()

    def _new_frame(self):
        return [ [ (0,0,0,0) for _ in range(self.pixel) ] for _ in range(self.pixel) ]

    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(side='top', fill='x', padx=8, pady=8)
        # Tools (ttk for a cleaner look)
        self.tool = 'pencil'
        ttk.Button(toolbar, text='Pencil', command=lambda: self.set_tool('pencil')).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Eraser', command=lambda: self.set_tool('eraser')).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Fill', command=lambda: self.set_tool('fill')).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Pick', command=lambda: self.set_tool('pick')).pack(side='left', padx=2)
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=6)
        ttk.Button(toolbar, text='New Frame', command=self.new_frame).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Dup Frame', command=self.duplicate_frame).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Del Frame', command=self.delete_frame).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Prev', command=self.prev_frame).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Next', command=self.next_frame).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Move<-', command=self.move_frame_left).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Move->', command=self.move_frame_right).pack(side='left', padx=2)
        ttk.Button(toolbar, text='Play', command=self.toggle_play).pack(side='left', padx=6)
        ttk.Button(toolbar, text='Export', command=self.export_frames).pack(side='left', padx=6)
        ttk.Button(toolbar, text='Export Sheet', command=self.export_spritesheet).pack(side='left', padx=2)
        # default onion skin from prefs if present
        self.onion_var = tk.BooleanVar(value=self._settings.get('onion', self._prefs.get('onion', False)))
        ttk.Checkbutton(toolbar, text='Onion Skin', variable=self.onion_var, command=self._redraw).pack(side='left', padx=6)

        main = tk.Frame(self)
        main.pack(fill='both', expand=True)

        right = tk.Frame(main)
        right.pack(side='right', fill='y', padx=6, pady=6)

        pal_frame = ttk.LabelFrame(right, text='Palette')
        pal_frame.pack(padx=2, pady=2, fill='x')
        # theme-aware palette buttons
        theme = getattr(self, 'theme', 'light')
        for i, c in enumerate(PALETTE):
            if c[3] == 0:
                colhex = '#2f2f2f' if theme == 'dark' else '#dddddd'
            else:
                colhex = '#%02x%02x%02x' % (c[0], c[1], c[2])
            # use tk.Button for direct background color, but make size/padding consistent
            b = tk.Button(pal_frame, bg=colhex, width=3, height=1, relief='flat', bd=1, command=lambda col=c: self.select_color(col))
            try:
                b.configure(highlightthickness=1, highlightbackground='#444444' if theme == 'dark' else '#e0e0e0')
            except Exception:
                pass
            b.grid(row=i//2, column=i%2, padx=4, pady=4)

        zoom_frame = tk.LabelFrame(right, text='Zoom')
        zoom_frame.pack(padx=2, pady=6)
        zscale = tk.Scale(zoom_frame, from_=4, to=20, orient='vertical', command=self.set_zoom)
        zscale.set(self.zoom)
        zscale.pack()

        # pixel size control
        tk.Label(right, text='Pixel Size:').pack()
        self.pixel_var = tk.IntVar(value=self.pixel)
        tk.Spinbox(right, from_=8, to=128, increment=8, textvariable=self.pixel_var, command=self.change_pixel_size).pack(padx=2, pady=2)

        # animations controls
        anim_frame = ttk.Frame(right)
        anim_frame.pack(padx=4, pady=8)
        ttk.Button(anim_frame, text='New Anim', command=self.new_animation).pack(side='left', padx=4)
        ttk.Button(anim_frame, text='Del Anim', command=self.delete_animation).pack(side='left', padx=4)
        ttk.Label(anim_frame, text=' Anim:').pack(side='left', padx=(6,2))
        self.anim_var = tk.StringVar(value=self.animations[self.current_anim]['name'])
        self.anim_menu = ttk.OptionMenu(anim_frame, self.anim_var, self.animations[self.current_anim]['name'], *[a['name'] for a in self.animations], command=self.select_animation)
        self.anim_menu.pack(side='left')

        canvas_frame = tk.Frame(main)
        canvas_frame.pack(side='left', padx=12, pady=12)

        canvas_bg = '#101010' if getattr(self, 'theme', 'light') == 'dark' else 'white'
        self.canvas = tk.Canvas(canvas_frame, width=self.pixel*self.zoom, height=self.pixel*self.zoom, bg=canvas_bg, highlightthickness=0)
        self.canvas.pack()
        # use press/motion/release handlers and draw interpolated lines for fast movement
        self._last_draw = None
        self.canvas.bind('<ButtonPress-1>', self._start_draw)
        self.canvas.bind('<B1-Motion>', self._draw_motion)
        self.canvas.bind('<ButtonRelease-1>', self._end_draw)
        self.canvas.bind('<Button-3>', self.canvas_pick)

        # simple behavior controls (exported to meta)
        behavior_frame = tk.LabelFrame(right, text='Behavior')
        behavior_frame.pack(padx=2, pady=6)
        # behavior dict exported to metadata
        self.behavior = {'follow_cursor': False, 'speed': 8, 'mode': 'stay'}
        # use ttk Checkbutton for better theme compatibility
        self.follow_var = tk.BooleanVar(value=self.behavior['follow_cursor'])
        ttk.Checkbutton(behavior_frame, text='Follow Cursor', variable=self.follow_var, command=self._sync_behavior).pack(anchor='w')
        tk.Label(behavior_frame, text='Mode:').pack(anchor='w')
        self.mode_var = tk.StringVar(value=self.behavior['mode'])
        modes = ['stay', 'follow', 'wander', 'circle', 'grab']
        self.mode_menu = ttk.OptionMenu(behavior_frame, self.mode_var, self.behavior['mode'], *modes, command=self._set_mode)
        self.mode_menu.pack(fill='x')
        tk.Label(behavior_frame, text='Speed:').pack(anchor='w')
        self.speed_scale = tk.Scale(behavior_frame, from_=1, to=60, orient='horizontal', command=self._set_speed)
        self.speed_scale.set(self.behavior['speed'])
        self.speed_scale.pack(fill='x')

        bottom = ttk.Frame(self)
        bottom.pack(side='bottom', fill='x')
        self.status = ttk.Label(bottom, text='Frame 1 / 1', padding=6)
        self.status.pack(fill='x', padx=6, pady=6)

    def set_zoom(self, z):
        self.zoom = int(z)
        self.canvas.config(width=self.pixel*self.zoom, height=self.pixel*self.zoom)
        self._redraw()

    def select_color(self, col):
        self.current_color = col

    def _redraw(self):
        # Compose onion skins if enabled
        img = Image.new('RGBA', (self.pixel,self.pixel), (0,0,0,0))
        if getattr(self, 'onion_var', None) and self.onion_var.get():
            # previous frame faint
            if self.current_frame - 1 >= 0:
                prev = self._get_frames()[self.current_frame-1]
                for y in range(self.pixel):
                    for x in range(self.pixel):
                        c = prev[y][x]
                        if c[3] != 0:
                            img.putpixel((x,y), (c[0], c[1], c[2], 120))
            # next frame faint overlay
            if self.current_frame + 1 < len(self._get_frames()):
                nxt = self._get_frames()[self.current_frame+1]
                for y in range(self.pixel):
                    for x in range(self.pixel):
                        c = nxt[y][x]
                        if c[3] != 0:
                            # blend over
                            base = img.getpixel((x,y))
                            img.putpixel((x,y), (c[0], c[1], c[2], 120))
        # draw current frame on top
        arr = self._get_frames()[self.current_frame]
        for y in range(self.pixel):
            for x in range(self.pixel):
                img.putpixel((x,y), arr[y][x])
        img = img.resize((self.pixel*self.zoom, self.pixel*self.zoom), Image.NEAREST)
        self.tkimg = ImageTk.PhotoImage(img)
        # clear canvas and redraw image + optional grid
        try:
            self.canvas.delete('all')
        except Exception:
            pass
        self.canvas.create_image(0,0,anchor='nw',image=self.tkimg)
        # draw grid lines to show pixel boundaries
        grid_color = '#3a3a3a' if getattr(self, 'theme', 'light') == 'dark' else '#cccccc'
        show_grid = True
        try:
            show_grid = load_settings().get('show_grid', True)
        except Exception:
            pass
        if self.zoom >= 6 and show_grid:
            w = self.pixel * self.zoom
            h = self.pixel * self.zoom
            for gx in range(0, w+1, self.zoom):
                self.canvas.create_line(gx, 0, gx, h, fill=grid_color)
            for gy in range(0, h+1, self.zoom):
                self.canvas.create_line(0, gy, w, gy, fill=grid_color)
        self.status.config(text=f'Frame {self.current_frame+1} / {len(self._get_frames())} (Anim: {self.animations[self.current_anim]["name"]})')

    def _get_frames(self):
        return self.animations[self.current_anim]['frames']

    def change_pixel_size(self):
        try:
            new = int(self.pixel_var.get())
        except Exception:
            return
        if new == self.pixel: return
        self.pixel = new
        # recreate current frames at new size (simple upscale/downscale: reset)
        self.animations = [{'name':a['name'], 'frames':[self._new_frame() for _ in a['frames']]} for a in self.animations]
        self.current_frame = 0
        self._redraw()

    def canvas_click(self, event):
        # legacy single-click handler — kept for compatibility but not used by main bindings
        x = int(event.x // self.zoom)
        y = int(event.y // self.zoom)
        self._draw_point(x, y)

    def _draw_point(self, x, y):
        if not (0 <= x < self.pixel and 0 <= y < self.pixel):
            return
        if self.tool == 'pencil':
            self._get_frames()[self.current_frame][y][x] = self.current_color
        elif self.tool == 'eraser':
            self._get_frames()[self.current_frame][y][x] = (0,0,0,0)
        elif self.tool == 'fill':
            target = self._get_frames()[self.current_frame][y][x]
            if target != self.current_color:
                self._flood_fill(self.current_frame, x, y, target, self.current_color)
        elif self.tool == 'pick':
            col = self._get_frames()[self.current_frame][y][x]
            if col[3] != 0:
                self.current_color = col
        self._redraw()

    def _start_draw(self, event):
        x = int(event.x // self.zoom)
        y = int(event.y // self.zoom)
        self._last_draw = (x, y)
        self._draw_point(x, y)

    def _end_draw(self, event):
        self._last_draw = None

    def _draw_motion(self, event):
        x = int(event.x // self.zoom)
        y = int(event.y // self.zoom)
        if self._last_draw is None:
            self._last_draw = (x, y)
            self._draw_point(x, y)
            return
        x0, y0 = self._last_draw
        dx = x - x0
        dy = y - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            xi = int(round(x0 + dx * (i / steps)))
            yi = int(round(y0 + dy * (i / steps)))
            if 0 <= xi < self.pixel and 0 <= yi < self.pixel:
                self._draw_point(xi, yi)
        self._last_draw = (x, y)

    def canvas_pick(self, event):
        # right click picks color under cursor
        x = int(event.x // self.zoom)
        y = int(event.y // self.zoom)
        if 0 <= x < self.pixel and 0 <= y < self.pixel:
            col = self._get_frames()[self.current_frame][y][x]
            if col[3] != 0:
                self.current_color = col
                self._redraw()

    def set_tool(self, t):
        self.tool = t

    def new_frame(self):
        self._get_frames().insert(self.current_frame+1, self._new_frame())
        self.current_frame += 1
        self._redraw()

    def delete_frame(self):
        if len(self._get_frames()) <= 1: return
        self._get_frames().pop(self.current_frame)
        self.current_frame = max(0, self.current_frame-1)
        self._redraw()

    def prev_frame(self):
        self.current_frame = max(0, self.current_frame-1)
        self._redraw()

    def next_frame(self):
        self.current_frame = min(len(self._get_frames())-1, self.current_frame+1)
        self._redraw()

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self._play_loop()

    def additional_play_loop(self):
        if not self.playing: return
        # cycle through frames
        self.current_frame = (self.current_frame + 1) % len(self._get_frames())
        self._redraw()
        # use configured animation speed when available
        try:
            delay = int(self._prefs.get('animation_speed', 150))
        except Exception:
            delay = 150
        self.after(delay, self._play_loop)

    def _play_loop(self):
        if not self.playing: return
        self.current_frame = (self.current_frame + 1) % len(self._get_frames())
        self._redraw()
        try:
            delay = int(self._prefs.get('animation_speed', 150))
        except Exception:
            delay = 150
        self.after(delay, self._play_loop)

    def export_frames(self):
        name = simpledialog.askstring('Export', 'Sprite name (no spaces):')
        if not name: return
        outdir = self.assets_var.get() if hasattr(self, 'assets_var') else DEFAULT_ASSET_DIR
        if not outdir:
            outdir = DEFAULT_ASSET_DIR
        os.makedirs(outdir, exist_ok=True)
        # export frames for each animation and write metadata
        exported = 0
        meta = {'behavior': self.behavior, 'animations': [a['name'] for a in self.animations], 'pixel': self.pixel}
        for anim in self.animations:
            anim_name = anim['name']
            for i, frame in enumerate(anim['frames']):
                img = Image.new('RGBA', (self.pixel,self.pixel), (0,0,0,0))
                for y in range(self.pixel):
                    for x in range(self.pixel):
                        img.putpixel((x,y), frame[y][x])
                path = os.path.join(outdir, f'{name}_{anim_name}_{i}.png')
                img.save(path)
                exported += 1
        try:
            # write a meta per-animation so spawner can load by group prefix
            for anim in self.animations:
                anim_name = anim['name']
                meta_path = os.path.join(outdir, f'{name}_{anim_name}_meta.json')
                with open(meta_path, 'w', encoding='utf-8') as mf:
                    json.dump({'behavior': self.behavior, 'anim': anim_name, 'pixel': self.pixel}, mf, indent=2)
        except Exception:
            pass
        # write an overall meta as well
        try:
            overall_meta = os.path.join(outdir, f'{name}_meta.json')
            with open(overall_meta, 'w', encoding='utf-8') as mf:
                json.dump(meta, mf, indent=2)
        except Exception:
            overall_meta = None

        messagebox.showinfo('Export', f'Exported {exported} frames to {outdir}')
        # attempt to refresh spawner list in the main app so the new sprite appears immediately
        try:
            auto_refresh = True
            try:
                auto_refresh = bool(self._prefs.get('auto_refresh', True))
            except Exception:
                auto_refresh = True
            if auto_refresh:
                refreshed = False
                parent = self
                while parent is not None:
                    if hasattr(parent, 'spawner'):
                        try:
                            parent.spawner.refresh()
                            refreshed = True
                        except Exception:
                            pass
                        break
                    parent = getattr(parent, 'master', None)
                if not refreshed:
                    try:
                        root = tk._default_root
                        if root and hasattr(root, 'spawner'):
                            root.spawner.refresh()
                            refreshed = True
                    except Exception:
                        pass
        except Exception:
            pass

    def duplicate_frame(self):
        copy = [row[:] for row in self._get_frames()[self.current_frame]]
        self._get_frames().insert(self.current_frame+1, copy)
        self.current_frame += 1
        self._redraw()

    def move_frame_left(self):
        i = self.current_frame
        if i > 0:
            f = self._get_frames()
            f[i-1], f[i] = f[i], f[i-1]
            self.current_frame -= 1
            self._redraw()

    def move_frame_right(self):
        i = self.current_frame
        if i < len(self._get_frames())-1:
            f = self._get_frames()
            f[i+1], f[i] = f[i], f[i+1]
            self.current_frame += 1
            self._redraw()

    def _flood_fill(self, frame_idx, x, y, target, replacement):
        if target == replacement: return
        stack = [(x,y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cy < 0 or cx >= self.pixel or cy >= self.pixel: continue
            if self._get_frames()[frame_idx][cy][cx] != target: continue
            self._get_frames()[frame_idx][cy][cx] = replacement
            stack.append((cx+1,cy))
            stack.append((cx-1,cy))
            stack.append((cx,cy+1))
            stack.append((cx,cy-1))

    def _sync_behavior(self):
        self.behavior['follow_cursor'] = bool(self.follow_var.get())
        # keep mode in sync: legacy follow checkbox toggles mode to follow/stay
        if self.behavior['follow_cursor']:
            self.mode_var.set('follow')
            self.behavior['mode'] = 'follow'
        else:
            if self.mode_var.get() == 'follow':
                self.mode_var.set('stay')
                self.behavior['mode'] = 'stay'

    def _set_speed(self, v):
        try:
            self.behavior['speed'] = int(v)
        except Exception:
            pass

    def _set_mode(self, v):
        try:
            self.behavior['mode'] = str(v)
        except Exception:
            pass

    # ----- animation management -----
    def _refresh_anim_menu(self):
        try:
            menu = self.anim_menu['menu']
            menu.delete(0, 'end')
            for a in self.animations:
                name = a['name']
                menu.add_command(label=name, command=lambda n=name: (self.anim_var.set(n), self.select_animation(n)))
        except Exception:
            pass

    def new_animation(self):
        name = simpledialog.askstring('New Animation', 'Animation name:')
        if not name: return
        self.animations.append({'name': name, 'frames': [self._new_frame()]})
        self.current_anim = len(self.animations)-1
        self.current_frame = 0
        self.anim_var.set(name)
        self._refresh_anim_menu()
        self._redraw()

    def delete_animation(self):
        if len(self.animations) <= 1:
            messagebox.showinfo('Delete', 'At least one animation required')
            return
        self.animations.pop(self.current_anim)
        self.current_anim = max(0, self.current_anim-1)
        self.current_frame = 0
        self.anim_var.set(self.animations[self.current_anim]['name'])
        self._refresh_anim_menu()
        self._redraw()

    def select_animation(self, name):
        for i,a in enumerate(self.animations):
            if a['name'] == name:
                self.current_anim = i
                self.current_frame = 0
                self.anim_var.set(name)
                self._redraw()
                break

    def export_spritesheet(self):
        name = simpledialog.askstring('Export Sheet', 'Sprite sheet name (no spaces):')
        if not name: return
        outdir = self.assets_var.get() if hasattr(self, 'assets_var') else DEFAULT_ASSET_DIR
        if not outdir:
            outdir = DEFAULT_ASSET_DIR
        os.makedirs(outdir, exist_ok=True)
        # export spritesheet for current animation
        frames = self._get_frames()
        cols = len(frames)
        sheet = Image.new('RGBA', (self.pixel*cols, self.pixel), (0,0,0,0))
        for i, frame in enumerate(frames):
            img = Image.new('RGBA', (self.pixel,self.pixel), (0,0,0,0))
            for y in range(self.pixel):
                for x in range(self.pixel):
                    img.putpixel((x,y), frame[y][x])
            sheet.paste(img, (i*self.pixel, 0))
        path = os.path.join(outdir, f'{name}_sheet.png')
        sheet.save(path)
        messagebox.showinfo('Export', f'Exported spritesheet to {path}')
        try:
            parent = self
            while parent is not None:
                if hasattr(parent, 'spawner'):
                    try:
                        parent.spawner.refresh()
                    except Exception:
                        pass
                    break
                parent = getattr(parent, 'master', None)
        except Exception:
            pass

# ----------------- Spawner Frame -----------------
def group_assets(asset_dir=DEFAULT_ASSET_DIR):
    groups = {}
    try:
        files = []
        if asset_dir and os.path.isdir(asset_dir):
            for f in os.listdir(asset_dir):
                if f.lower().endswith('.png'):
                    files.append(os.path.join(asset_dir, f))
        else:
            files = glob.glob(asset_glob_pattern(asset_dir))
        for path in files:
            fname = os.path.basename(path)
            name, ext = os.path.splitext(fname)
            if '_' in name:
                prefix, idx = name.rsplit('_',1)
            else:
                prefix, idx = name, '0'
            groups.setdefault(prefix, []).append((int(idx) if idx.isdigit() else 0, path))
    except Exception:
        return {}
    out = {}
    for k,v in groups.items():
        v.sort()
        out[k] = [p for i,p in v]
    return out

class PetWindow(tk.Toplevel):
    def __init__(self, master, frames, x=100, y=100, behavior=None):
        super().__init__(master)
        self.overrideredirect(True)
        # respect global preference for pet windows always-on-top
        try:
            _global_settings = load_settings()
            topmost_pref = bool(_global_settings.get('always_on_top', True))
        except Exception:
            topmost_pref = True
        try:
            self.attributes('-topmost', topmost_pref)
        except Exception:
            pass
        try:
            self.wm_attributes('-transparentcolor', 'magenta')
        except Exception:
            pass
        # respect saved scale/animation_speed preferences
        s = load_settings()
        _scale = int(s.get('scale', SCALE))
        self._anim_delay = int(s.get('animation_speed', 120))
        self.frames = [Image.open(p).convert('RGBA') for p in frames]
        self.tkframes = [ImageTk.PhotoImage(f.resize((f.width*_scale, f.height*_scale), Image.NEAREST)) for f in self.frames]
        self.label = tk.Label(self, bg='magenta', bd=0, highlightthickness=0)
        self.label.pack()
        self.frame_idx = 0
        self.behavior = behavior or {}
        # normalize behavior dict (ensure expected keys/types)
        try:
            self.behavior['mode'] = str(self.behavior.get('mode', 'stay'))
        except Exception:
            self.behavior['mode'] = 'stay'
        try:
            self.behavior['speed'] = int(self.behavior.get('speed', 8))
        except Exception:
            self.behavior['speed'] = 8
        self.behavior['follow_cursor'] = bool(self.behavior.get('follow_cursor', False))
        # allow per-sprite animation speed override via meta
        try:
            if 'animation_speed' in self.behavior:
                self._anim_delay = int(self.behavior.get('animation_speed', self._anim_delay))
        except Exception:
            pass
        # initial geometry and position
        try:
            self.geometry(f'+{x}+{y}')
        except Exception:
            pass
        self._pos_x = float(x)
        self._pos_y = float(y)
        self._target_x = float(x)
        self._target_y = float(y)
        self._movement_interval = 30
        self._alive = True
        self.bind('<Destroy>', lambda e: setattr(self, '_alive', False))
        # movement helpers
        self._wander_target = None
        self._circle_state = None
        # start movement loop and animation
        self.after(self._movement_interval, self._movement_tick)
        self.animate()
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.do_drag)
        self.label.bind('<Button-3>', lambda e: self.destroy())

    def animate(self):
        if not self.tkframes: return
        self.label.config(image=self.tkframes[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % len(self.tkframes)
        # movement update
        self._apply_behavior()
        # allow behavior/meta to override animation delay
        try:
            delay = int(self.behavior.get('animation_speed', getattr(self, '_anim_delay', 120)))
        except Exception:
            try:
                delay = int(getattr(self, '_anim_delay', 120))
            except Exception:
                delay = 120
        self.after(delay, self.animate)

    def _movement_tick(self):
        if not getattr(self, '_alive', True):
            return
        try:
            import math
            dx = self._target_x - self._pos_x
            dy = self._target_y - self._pos_y
            dist = math.hypot(dx, dy)
            if dist <= 0.5:
                self._pos_x = float(self._target_x)
                self._pos_y = float(self._target_y)
            else:
                movement_interval = getattr(self, '_movement_interval', 30)
                step = max(0.5, self.behavior.get('speed', 8) * (movement_interval / 100.0))
                if dist <= step:
                    self._pos_x = float(self._target_x)
                    self._pos_y = float(self._target_y)
                else:
                    self._pos_x += dx / dist * step
                    self._pos_y += dy / dist * step
            try:
                self.geometry(f'+{int(round(self._pos_x))}+{int(round(self._pos_y))}')
            except Exception:
                pass
        except Exception:
            pass
        if getattr(self, '_alive', True):
            self.after(getattr(self, '_movement_interval', 30), self._movement_tick)

    def _apply_behavior(self):
        # improved movement logic: smooth follow, wander target, circle, and grab
        try:
            mode = (self.behavior or {}).get('mode', 'stay')
            # backward-compatible: honor explicit follow_cursor flag
            if (self.behavior or {}).get('follow_cursor'):
                mode = 'follow'
            speed = int(self.behavior.get('speed', 8))
            # use float positions for smoother motion
            wx = getattr(self, '_pos_x', float(self.winfo_x()))
            wy = getattr(self, '_pos_y', float(self.winfo_y()))
            # frame size (in case we need centering)
            fw = self.tkframes[0].width() if self.tkframes else 32
            fh = self.tkframes[0].height() if self.tkframes else 32
            import math, random
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()

            if mode == 'stay':
                return

            if mode == 'follow':
                px = self.winfo_pointerx()
                py = self.winfo_pointery()
                # target so pet centers on the cursor
                tx = px - fw//2
                ty = py - fh//2
                tx = max(0, min(tx, sw - fw))
                ty = max(0, min(ty, sh - fh))
                self._target_x, self._target_y = float(tx), float(ty)

            elif mode == 'wander':
                # pick a wandering target and move toward it
                if not getattr(self, '_wander_target', None):
                    tx = random.randint(0, max(0, sw - fw))
                    ty = random.randint(0, max(0, sh - fh))
                    self._wander_target = (tx, ty)
                tx, ty = self._wander_target
                self._target_x, self._target_y = float(tx), float(ty)
                # clear the wander target when reached
                if abs(tx - wx) <= speed and abs(ty - wy) <= speed:
                    self._wander_target = None

            elif mode == 'circle':
                if not getattr(self, '_circle_state', None):
                    self._circle_state = {'angle': 0, 'cx': wx, 'cy': wy, 'r': 80}
                cs = self._circle_state
                cs['angle'] = (cs['angle'] + speed/6) % 360
                a = math.radians(cs['angle'])
                tx = int(cs['cx'] + math.cos(a) * cs['r'])
                ty = int(cs['cy'] + math.sin(a) * cs['r'])
                tx = max(0, min(tx, sw - fw))
                ty = max(0, min(ty, sh - fh))
                self._target_x, self._target_y = float(tx), float(ty)

            elif mode == 'grab':
                px = self.winfo_pointerx()
                py = self.winfo_pointery()
                dx = px - wx
                dy = py - wy
                dist = math.hypot(dx, dy) or 0.0001
                if dist < 50:
                    # move to cursor immediately then set a far target
                    try:
                        self._target_x, self._target_y = float(px), float(py)
                    except Exception:
                        pass
                    angle = random.random() * 2 * math.pi
                    run_dist = 400
                    tx = int(px + math.cos(angle) * run_dist)
                    ty = int(py + math.sin(angle) * run_dist)
                    tx = max(0, min(tx, sw - fw))
                    ty = max(0, min(ty, sh - fh))
                    self._wander_target = (tx, ty)
                else:
                    tx = int(wx + dx / dist * min(speed, abs(dx)))
                    ty = int(wy + dy / dist * min(speed, abs(dy)))
                    tx = max(0, min(tx, sw - fw))
                    ty = max(0, min(ty, sh - fh))
                    self._target_x, self._target_y = float(tx), float(ty)
        except Exception:
            pass

    def start_drag(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def do_drag(self, e):
        x = self.winfo_x() + (e.x - self._drag_x)
        y = self.winfo_y() + (e.y - self._drag_y)
        # update float position and target for smooth movement
        try:
            self._pos_x = float(x)
            self._pos_y = float(y)
            self._target_x = float(x)
            self._target_y = float(y)
        except Exception:
            pass
        try:
            self.geometry(f'+{x}+{y}')
        except Exception:
            pass

class SpawnerFrame(tk.Frame):
    def __init__(self, master, assets_var: tk.StringVar):
        super().__init__(master)
        self.assets_var = assets_var
        self.groups = group_assets(self.assets_var.get())
        tk.Label(self, text='Available Sprites:').pack(anchor='w')
        self.listbox = tk.Listbox(self)
        for k in sorted(self.groups.keys()):
            self.listbox.insert('end', k)
        self.listbox.pack(fill='both', expand=True)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=6)
        ttk.Button(btn_frame, text='Spawn', command=self.spawn_selected).pack(side='left', padx=6)
        ttk.Button(btn_frame, text='Refresh', command=self.refresh).pack(side='left')
        ttk.Button(btn_frame, text='Build EXE', command=self.build_selected).pack(side='left', padx=6)
        # Folder selector
        ttk.Label(btn_frame, text=' Folder:').pack(side='left', padx=(8,2))
        self.folder_entry = ttk.Entry(btn_frame, width=24, textvariable=self.assets_var)
        self.folder_entry.pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Browse', command=self.browse_folder).pack(side='left', padx=6)
        self.info = ttk.Label(self, text='Right-click pet to close it. Drag to move.')
        self.info.pack(pady=(6,2))

    def refresh(self):
        self.groups = group_assets(self.assets_var.get())
        self.listbox.delete(0,'end')
        for k in sorted(self.groups.keys()):
            self.listbox.insert('end', k)

    def spawn_selected(self):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        frames = self.groups.get(name)
        if not frames: return
        import random
        sw = self.winfo_screenwidth()
        x = random.randint(50, max(50, sw-200))
        y = 100
        # try to load metadata for this sprite; be flexible about meta filename
        behavior = None
        loaded_meta = None
        try:
            asset_dir = self.assets_var.get() or DEFAULT_ASSET_DIR
            candidates = [
                os.path.join(asset_dir, f'{name}_meta.json'),
                os.path.join(asset_dir, f'{name}.json'),
                os.path.join(asset_dir, f'{name}_meta.JSON')
            ]
            # try primary candidates first
            for c in candidates:
                if os.path.exists(c):
                    with open(c, 'r', encoding='utf-8') as mf:
                        m = json.load(mf)
                        b = m.get('behavior') if isinstance(m, dict) else None
                        if isinstance(b, dict):
                            behavior = b.copy()
                        else:
                            # accept top-level keys as fallback
                            behavior = {}
                            if isinstance(m, dict):
                                if 'mode' in m: behavior['mode'] = m.get('mode')
                                if 'speed' in m: behavior['speed'] = m.get('speed')
                                if 'follow_cursor' in m: behavior['follow_cursor'] = m.get('follow_cursor')
                                if 'animation_speed' in m: behavior['animation_speed'] = m.get('animation_speed')
                        loaded_meta = c
                        break
            # broader glob matches
            if behavior is None:
                for p in glob.glob(os.path.join(asset_dir, f'{name}*_meta.json')):
                    try:
                        with open(p, 'r', encoding='utf-8') as mf:
                            m = json.load(mf)
                            b = m.get('behavior') if isinstance(m, dict) else None
                            behavior = b.copy() if isinstance(b, dict) else {}
                            loaded_meta = p
                            break
                    except Exception:
                        continue
            # fallback to prefix meta (hero_idle -> hero_meta.json)
            if behavior is None and '_' in name:
                prefix = name.rsplit('_',1)[0]
                p = os.path.join(asset_dir, f'{prefix}_meta.json')
                if os.path.exists(p):
                    try:
                        with open(p, 'r', encoding='utf-8') as mf:
                            m = json.load(mf)
                            b = m.get('behavior') if isinstance(m, dict) else None
                            behavior = b.copy() if isinstance(b, dict) else {}
                            loaded_meta = p
                    except Exception:
                        behavior = {}
        except Exception:
            behavior = {}

        # ensure behavior is a dict and normalize expected fields
        behavior = behavior or {}
        try:
            behavior['mode'] = str(behavior.get('mode', 'stay'))
        except Exception:
            behavior['mode'] = 'stay'
        try:
            behavior['speed'] = int(behavior.get('speed', 8))
        except Exception:
            behavior['speed'] = 8
        # support alternative keys for follow
        if 'follow_cursor' not in behavior:
            behavior['follow_cursor'] = bool(behavior.get('follow', behavior.get('followCursor', False)))
        # normalize animation speed if present
        if 'animation_speed' in behavior:
            try:
                behavior['animation_speed'] = int(behavior['animation_speed'])
            except Exception:
                del behavior['animation_speed']
        # show a small status about loaded meta
        try:
            if loaded_meta:
                self.info.config(text=f'Loaded meta: {os.path.basename(loaded_meta)}')
            else:
                self.info.config(text='No meta found for this sprite (using defaults)')
        except Exception:
            pass
        PetWindow(self, frames, x, y, behavior=behavior)

    def build_selected(self):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        frames = self.groups.get(name)
        if not frames: return
        # ask where to save the final exe (or zip if pyinstaller missing)
        target = filedialog.asksaveasfilename(defaultextension='.exe', initialfile=f'{name}.exe', title='Save EXE as')
        if not target:
            return
        exe_basename = os.path.splitext(os.path.basename(target))[0]
        build_dir = tempfile.mkdtemp(prefix=f'pet_build_{exe_basename}_')
        try:
            # copy frames into build dir as frame_0.png, frame_1.png, ...
            for i, p in enumerate(frames):
                try:
                    dst = os.path.join(build_dir, f'frame_{i}.png')
                    shutil.copy2(p, dst)
                except Exception:
                    pass
            # gather behavior (try to load meta if present)
            behavior = {}
            # try meta files next to first frame
            try:
                first_dir = os.path.dirname(frames[0]) if frames else os.getcwd()
                candidates = [
                    os.path.join(first_dir, f'{name}_meta.json'),
                    os.path.join(first_dir, f'{name}.json')
                ]
                for c in candidates:
                    if os.path.exists(c):
                        try:
                            with open(c, 'r', encoding='utf-8') as mf:
                                m = json.load(mf)
                                if isinstance(m, dict) and 'behavior' in m and isinstance(m['behavior'], dict):
                                    behavior = m['behavior'].copy()
                                    break
                        except Exception:
                            continue
            except Exception:
                behavior = {}
            # write a minimal launcher script into build_dir
            try:
                behavior_json = json.dumps(behavior)
                launcher = _STANDALONE_LAUNCHER_TEMPLATE.replace('{BEHAVIOR_JSON}', behavior_json)
                with open(os.path.join(build_dir, 'run_pet.py'), 'w', encoding='utf-8') as rf:
                    rf.write(launcher)
            except Exception:
                messagebox.showerror('Error', 'Failed to write launcher script')
                return

            # try to build with PyInstaller using the current Python
            pyinstaller_cmd = [sys.executable, '-m', 'PyInstaller']
            can_run_pyinstaller = shutil.which('pyinstaller') is not None
            if not can_run_pyinstaller:
                # try python -m PyInstaller check
                try:
                    res = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], capture_output=True, text=True)
                    can_run_pyinstaller = (res.returncode == 0)
                except Exception:
                    can_run_pyinstaller = False

            if can_run_pyinstaller:
                args = [sys.executable, '-m', 'PyInstaller', '--onefile', '--noconsole', '--name', exe_basename]
                # add data args for frames
                for i in range(len(frames)):
                    args += ['--add-data', f'frame_{i}.png;.']
                args.append('run_pet.py')
                try:
                    proc = subprocess.run(args, cwd=build_dir, capture_output=True, text=True)
                    if proc.returncode == 0:
                        built = os.path.join(build_dir, 'dist', exe_basename + '.exe')
                        if os.path.exists(built):
                            try:
                                shutil.copy2(built, target)
                                messagebox.showinfo('Build complete', f'Executable created: {target}')
                                return
                            except Exception:
                                messagebox.showwarning('Built', f'Built exe at {built} but failed to copy to {target}')
                                return
                        else:
                            messagebox.showerror('PyInstaller', 'PyInstaller reported success but exe not found')
                            return
                    else:
                        out = proc.stdout + '\n' + proc.stderr
                        messagebox.showerror('PyInstaller failed', f'PyInstaller failed:\n{out}')
                        return
                except Exception as e:
                    messagebox.showerror('Error', f'Failed to run PyInstaller: {e}')
                    return
            else:
                # fallback: zip the build dir and instruct the user how to run PyInstaller
                zip_path = os.path.join(os.path.dirname(target), exe_basename + '_build.zip')
                try:
                    shutil.make_archive(os.path.splitext(zip_path)[0], 'zip', build_dir)
                    cmd = f'cd {build_dir}\n{sys.executable} -m PyInstaller --onefile --noconsole --add-data "frame_0.png;." run_pet.py'
                    messagebox.showinfo('Build ready', f'Created build folder zip: {zip_path}\n\nPyInstaller not found. To create an exe, extract the zip and run:\n{cmd}')
                except Exception as e:
                    messagebox.showerror('Error', f'Failed to create build zip: {e}')
                return

        finally:
            # leave build_dir for inspection; do not remove automatically
            pass

    def browse_folder(self):
        d = filedialog.askdirectory(initialdir=self.assets_var.get() or os.getcwd(), title='Select assets folder')
        if d:
            self.assets_var.set(d)
            self.refresh()


class PresetsFrame(tk.Frame):
    def __init__(self, master, presets_var: tk.StringVar):
        super().__init__(master)
        self.presets_var = presets_var
        self.groups = group_assets(self.presets_var.get())
        tk.Label(self, text='Preset Collections:').pack(anchor='w')
        self.listbox = tk.Listbox(self)
        for k in sorted(self.groups.keys()):
            self.listbox.insert('end', k)
        self.listbox.pack(fill='both', expand=True)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=6)
        ttk.Button(btn_frame, text='Spawn Preset', command=self.spawn_selected).pack(side='left', padx=6)
        ttk.Button(btn_frame, text='Refresh', command=self.refresh).pack(side='left')
        ttk.Label(btn_frame, text=' Folder:').pack(side='left', padx=(8,2))
        self.folder_entry = ttk.Entry(btn_frame, width=30, textvariable=self.presets_var)
        self.folder_entry.pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Browse', command=self.browse_folder).pack(side='left', padx=6)
        tk.Label(self, text='Presets are grouped by name (name_0.png, name_1.png...) in the selected folder').pack(pady=6)

    def refresh(self):
        self.groups = group_assets(self.presets_var.get())
        self.listbox.delete(0,'end')
        for k in sorted(self.groups.keys()):
            self.listbox.insert('end', k)

    def spawn_selected(self):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        frames = self.groups.get(name)
        if not frames: return
        import random
        sw = self.winfo_screenwidth()
        x = random.randint(50, max(50, sw-200))
        y = 100
        PetWindow(self, frames, x, y)

    def browse_folder(self):
        d = filedialog.askdirectory(initialdir=self.presets_var.get() or os.getcwd(), title='Select presets folder')
        if d:
            self.presets_var.set(d)
            self.refresh()


# Template for the standalone launcher script; {BEHAVIOR_JSON} is replaced with JSON-serialized behavior
_STANDALONE_LAUNCHER_TEMPLATE = """import tkinter as tk
from PIL import Image, ImageTk
import json, os, math, random, sys

behavior = json.loads('''{BEHAVIOR_JSON}''')

def load_frames():
    files = sorted([f for f in os.listdir('.') if f.startswith('frame_') and f.lower().endswith('.png')], key=lambda s: int(s.split('_')[1].split('.')[0]))
    frames = []
    for f in files:
        try:
            frames.append(Image.open(f).convert('RGBA'))
        except Exception:
            pass
    return frames

def main():
    frames = load_frames()
    if not frames:
        print('No frames found')
        return
    scale = int(behavior.get('scale', 4))
    tk_frames = [ImageTk.PhotoImage(im.resize((im.width*scale, im.height*scale), Image.NEAREST)) for im in frames]
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    try:
        root.wm_attributes('-transparentcolor', 'magenta')
    except Exception:
        pass
    label = tk.Label(root, bg='magenta', bd=0)
    label.pack()
    state = {'pos_x':100.0, 'pos_y':100.0, 'target_x':100.0, 'target_y':100.0, 'frame_idx':0}
    movement_interval = 30
    def animate():
        idx = state['frame_idx'] % len(tk_frames)
        label.config(image=tk_frames[idx])
        state['frame_idx'] += 1
        delay = int(behavior.get('animation_speed', 120))
        root.after(delay, animate)
    def movement_tick():
        dx = state['target_x'] - state['pos_x']
        dy = state['target_y'] - state['pos_y']
        dist = math.hypot(dx, dy)
        if dist > 0.5:
            step = max(0.5, behavior.get('speed', 8) * (movement_interval / 100.0))
            if dist <= step:
                state['pos_x'] = state['target_x']; state['pos_y'] = state['target_y']
            else:
                state['pos_x'] += dx/dist*step; state['pos_y'] += dy/dist*step
            try:
                root.geometry(f'+{int(round(state["pos_x"]))}+{int(round(state["pos_y"]))}')
            except Exception:
                pass
        root.after(movement_interval, movement_tick)
    def update_behavior_target():
        mode = behavior.get('mode','stay')
        if behavior.get('follow_cursor') or mode=='follow':
            px = root.winfo_pointerx(); py = root.winfo_pointery()
            tx = px - tk_frames[0].width()//2; ty = py - tk_frames[0].height()//2
            sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
            tx = max(0, min(tx, sw - tk_frames[0].width())); ty = max(0, min(ty, sh - tk_frames[0].height()))
            state['target_x'] = float(tx); state['target_y'] = float(ty)
        elif mode == 'wander':
            if not hasattr(update_behavior_target, 'wander_target'):
                sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
                update_behavior_target.wander_target = (random.randint(0, max(0, sw - tk_frames[0].width())), random.randint(0, max(0, sh - tk_frames[0].height())))
            tx, ty = update_behavior_target.wander_target
            state['target_x'] = float(tx); state['target_y'] = float(ty)
            if abs(tx - state['pos_x']) <= behavior.get('speed',8) and abs(ty - state['pos_y']) <= behavior.get('speed',8):
                update_behavior_target.wander_target = None
        elif mode == 'circle':
            if not hasattr(update_behavior_target, 'circle_state'):
                update_behavior_target.circle_state = {'angle':0, 'cx':state['pos_x'], 'cy':state['pos_y'], 'r':80}
            cs = update_behavior_target.circle_state
            cs['angle'] = (cs['angle'] + behavior.get('speed',8)/6) % 360
            a = math.radians(cs['angle'])
            tx = int(cs['cx'] + math.cos(a) * cs['r']); ty = int(cs['cy'] + math.sin(a) * cs['r'])
            sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
            tx = max(0, min(tx, sw - tk_frames[0].width())); ty = max(0, min(ty, sh - tk_frames[0].height()))
            state['target_x'] = float(tx); state['target_y'] = float(ty)
        elif mode == 'grab':
            px = root.winfo_pointerx(); py = root.winfo_pointery()
            dx = px - state['pos_x']; dy = py - state['pos_y']
            dist = math.hypot(dx, dy) or 0.0001
            if dist < 50:
                state['target_x'] = float(px); state['target_y'] = float(py)
                angle = random.random() * 2 * math.pi
                tx = int(px + math.cos(angle) * 400); ty = int(py + math.sin(angle) * 400)
                sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
                tx = max(0, min(tx, sw - tk_frames[0].width())); ty = max(0, min(ty, sh - tk_frames[0].height()))
                update_behavior_target.wander_target = (tx, ty)
            else:
                tx = int(state['pos_x'] + dx/dist * min(behavior.get('speed',8), abs(dx)))
                ty = int(state['pos_y'] + dy/dist * min(behavior.get('speed',8), abs(dy)))
                sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
                tx = max(0, min(tx, sw - tk_frames[0].width())); ty = max(0, min(ty, sh - tk_frames[0].height()))
                state['target_x'] = float(tx); state['target_y'] = float(ty)
        root.after(200, update_behavior_target)
    root.geometry(f'+{int(state["pos_x"])}+{int(state["pos_y"])}')
    animate(); movement_tick(); update_behavior_target()
    root.mainloop()

if __name__ == '__main__':
    main()
"""


class MakerWindow(tk.Toplevel):
    def __init__(self, master, assets_var, settings=None):
        super().__init__(master)
        self.title('Maker')
        self.geometry('600x520')
        self.maker = MakerFrame(self, assets_var, settings=settings)
        self.maker.pack(fill='both', expand=True)

        # apply theme to this Toplevel
        try:
            apply_ui_theme(self, theme=(settings or {}).get('theme', 'light'))
        except Exception:
            apply_ui_theme(self)

# ----------------- Combined App -----------------
class PetToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Pet Maker + Spawner')
        self.geometry('900x600')
        # load and apply saved settings
        self.settings = load_settings()
        apply_ui_theme(self, theme=self.settings.get('theme', 'light'))
        # set a nicer default font for native widgets too
        try:
            default_font = tkfont.nametofont('TkDefaultFont')
            default_font.configure(size=10, family='Segoe UI')
        except Exception:
            pass
        # assets folder selector (respect saved setting)
        self.settings = load_settings()
        self.assets_var = tk.StringVar(value=self.settings.get('assets_dir', DEFAULT_ASSET_DIR))
        # presets folder (defaults to assets/presets)
        self.presets_var = tk.StringVar(value=os.path.join(self.assets_var.get(), 'presets'))
        top = ttk.Frame(self)
        top.pack(side='top', fill='x', padx=8, pady=8)
        ttk.Label(top, text='Assets folder:').pack(side='left')
        self.assets_entry = ttk.Entry(top, textvariable=self.assets_var, width=40)
        self.assets_entry.pack(side='left', padx=6)
        ttk.Button(top, text='Browse', command=self.browse_assets).pack(side='left')

        # Menubar
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label='Open Maker', command=lambda: MakerWindow(self, self.assets_var, settings=self.settings))
        filem.add_separator()
        filem.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=filem)
        # Edit / Preferences
        editm = tk.Menu(menubar, tearoff=0)
        editm.add_command(label='Preferences', command=self.open_preferences)
        menubar.add_cascade(label='Edit', menu=editm)
        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label='About', command=self.show_about)
        menubar.add_cascade(label='Help', menu=helpm)
        self.config(menu=menubar)

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)
        # Maker runs in its own window; provide a launcher in the notebook
        maker_placeholder = ttk.Frame(nb, padding=16)
        def open_maker():
            MakerWindow(self, self.assets_var, settings=self.settings)
        ttk.Label(maker_placeholder, text='Open the Maker in a separate window to edit sprites.').pack(pady=10)
        ttk.Button(maker_placeholder, text='Open Maker', command=open_maker).pack()
        self.maker = None
        self.spawner = SpawnerFrame(nb, self.assets_var)
        self.presets = PresetsFrame(nb, self.presets_var)
        nb.add(maker_placeholder, text='Maker')
        nb.add(self.spawner, text='Spawner')
        nb.add(self.presets, text='Presets')

        # status bar
        self.status_var = tk.StringVar(value='Ready')
        status = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w', padding=6)
        status.pack(side='bottom', fill='x')

    def open_preferences(self):
        d = tk.Toplevel(self)
        d.title('Preferences')
        d.geometry('320x220')
        # layout variables
        frame = ttk.Frame(d, padding=12)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Theme:').grid(row=0, column=0, sticky='w')
        theme_var = tk.StringVar(value=self.settings.get('theme', 'light'))
        ttk.Radiobutton(frame, text='Light', variable=theme_var, value='light').grid(row=1, column=0, sticky='w', pady=2)
        ttk.Radiobutton(frame, text='Dark', variable=theme_var, value='dark').grid(row=1, column=1, sticky='w', pady=2)

        ttk.Label(frame, text='Default Pixel Size:').grid(row=2, column=0, sticky='w', pady=(8,0))
        def_pix = tk.IntVar(value=self.settings.get('default_pixel', PIXEL))
        ttk.Spinbox(frame, from_=8, to=128, increment=4, textvariable=def_pix, width=8).grid(row=3, column=0, sticky='w')

        ttk.Label(frame, text='Default Zoom:').grid(row=2, column=1, sticky='w', pady=(8,0))
        def_zoom = tk.IntVar(value=self.settings.get('default_zoom', DEFAULT_ZOOM))
        ttk.Spinbox(frame, from_=4, to=32, increment=1, textvariable=def_zoom, width=8).grid(row=3, column=1, sticky='w')

        # more preferences
        ttk.Label(frame, text='Accent Color:').grid(row=4, column=0, sticky='w', pady=(8,0))
        accent_var = tk.StringVar(value=self.settings.get('accent', 'blue'))
        accent_menu = ttk.OptionMenu(frame, accent_var, self.settings.get('accent', 'blue'), 'blue', 'teal', 'purple', 'orange', 'pink')
        accent_menu.grid(row=5, column=0, sticky='w')

        show_grid_var = tk.BooleanVar(value=self.settings.get('show_grid', True))
        ttk.Checkbutton(frame, text='Show Pixel Grid', variable=show_grid_var).grid(row=4, column=1, sticky='w')

        onion_var = tk.BooleanVar(value=self.settings.get('onion', False))
        ttk.Checkbutton(frame, text='Onion Skin Enabled', variable=onion_var).grid(row=5, column=1, sticky='w')

        ttk.Label(frame, text='Default Assets Folder:').grid(row=6, column=0, sticky='w', pady=(8,0))
        assets_var = tk.StringVar(value=self.settings.get('assets_dir', self.assets_var.get()))
        assets_entry = ttk.Entry(frame, textvariable=assets_var, width=26)
        assets_entry.grid(row=7, column=0, sticky='w')
        def browse_assets_pref():
            ddir = filedialog.askdirectory(initialdir=assets_var.get() or os.getcwd(), title='Select assets folder')
            if ddir:
                assets_var.set(ddir)
        ttk.Button(frame, text='Browse', command=browse_assets_pref).grid(row=7, column=1, sticky='w')

        ttk.Label(frame, text='Pet Scale:').grid(row=8, column=0, sticky='w', pady=(8,0))
        scale_var = tk.IntVar(value=self.settings.get('scale', SCALE))
        ttk.Spinbox(frame, from_=1, to=8, increment=1, textvariable=scale_var, width=6).grid(row=9, column=0, sticky='w')

        ttk.Label(frame, text='Animation Delay (ms):').grid(row=8, column=1, sticky='w', pady=(8,0))
        anim_var = tk.IntVar(value=self.settings.get('animation_speed', 120))
        ttk.Spinbox(frame, from_=30, to=1000, increment=10, textvariable=anim_var, width=8).grid(row=9, column=1, sticky='w')

        # additional preferences
        auto_refresh_var = tk.BooleanVar(value=self.settings.get('auto_refresh', True))
        ttk.Checkbutton(frame, text='Auto-refresh spawner after export', variable=auto_refresh_var).grid(row=10, column=0, sticky='w', pady=(8,0))
        always_on_top_var = tk.BooleanVar(value=self.settings.get('always_on_top', True))
        ttk.Checkbutton(frame, text='Pets Always On Top', variable=always_on_top_var).grid(row=10, column=1, sticky='w', pady=(8,0))

        def apply_prefs():
            self.settings['theme'] = theme_var.get()
            try:
                self.settings['default_pixel'] = int(def_pix.get())
            except Exception:
                self.settings['default_pixel'] = PIXEL
            try:
                self.settings['default_zoom'] = int(def_zoom.get())
            except Exception:
                self.settings['default_zoom'] = DEFAULT_ZOOM
            # new prefs
            try:
                self.settings['accent'] = str(accent_var.get())
            except Exception:
                pass
            try:
                self.settings['show_grid'] = bool(show_grid_var.get())
            except Exception:
                pass
            try:
                self.settings['onion'] = bool(onion_var.get())
            except Exception:
                pass
            try:
                self.settings['assets_dir'] = str(assets_var.get())
            except Exception:
                pass
            try:
                self.settings['scale'] = int(scale_var.get())
            except Exception:
                self.settings['scale'] = SCALE
            try:
                self.settings['animation_speed'] = int(anim_var.get())
            except Exception:
                self.settings['animation_speed'] = 120
            try:
                self.settings['auto_refresh'] = bool(auto_refresh_var.get())
            except Exception:
                pass
            try:
                self.settings['always_on_top'] = bool(always_on_top_var.get())
            except Exception:
                pass
            save_settings(self.settings)
            apply_ui_theme(self, theme=self.settings.get('theme', 'light'))
            # update assets var and presets var
            try:
                self.assets_var.set(self.settings.get('assets_dir', self.assets_var.get()))
                self.presets_var.set(os.path.join(self.assets_var.get(), 'presets'))
            except Exception:
                pass
            # refresh spawner/presets immediately when prefs change
            try:
                if hasattr(self, 'spawner') and getattr(self, 'spawner') is not None:
                    try:
                        self.spawner.refresh()
                    except Exception:
                        pass
                if hasattr(self, 'presets') and getattr(self, 'presets') is not None:
                    try:
                        self.presets.refresh()
                    except Exception:
                        pass
            except Exception:
                pass
            # update any open Maker windows
            try:
                for w in self.winfo_children():
                    if isinstance(w, MakerWindow):
                        apply_ui_theme(w, theme=self.settings.get('theme', 'light'))
                        if hasattr(w, 'maker') and isinstance(w.maker, MakerFrame):
                            w.maker.pixel = self.settings.get('default_pixel', w.maker.pixel)
                            w.maker.zoom = self.settings.get('default_zoom', w.maker.zoom)
                            w.maker.pixel_var.set(w.maker.pixel)
                            # update maker onion default and prefs cache
                            try:
                                w.maker.onion_var.set(self.settings.get('onion', w.maker.onion_var.get()))
                                w.maker._prefs = self.settings
                            except Exception:
                                pass
                            w.maker._redraw()
            except Exception:
                pass
            self.status_var.set('Preferences saved')
            d.destroy()

        btn_frame = ttk.Frame(d)
        btn_frame.pack(side='bottom', fill='x', pady=12)
        ttk.Button(btn_frame, text='Save', command=apply_prefs).pack(side='right', padx=8)
        ttk.Button(btn_frame, text='Cancel', command=d.destroy).pack(side='right')

    def show_about(self):
        # show a small about dialog with a clickable link
        d = tk.Toplevel(self)
        d.title('About')
        d.geometry('420x160')
        d.resizable(False, False)
        tk.Label(d, text='Pet Maker + Spawner', font=('Segoe UI', 12, 'bold')).pack(pady=(8,0))
        tk.Label(d, text='A small tool for creating and spawning pixel pets.').pack(pady=(6,4))
        tk.Label(d, text='Made by ehjarvis_alt on GitHub!').pack()
        link = tk.Label(d, text='https://github.com/ehjarvis_alt', fg='blue', cursor='hand2')
        link.pack(pady=6)
        def open_link(e=None):
            webbrowser.open('https://github.com/ehjarvis_alt')
        link.bind('<Button-1>', open_link)
        btn = ttk.Button(d, text='Open on GitHub', command=open_link)
        btn.pack(pady=(4,8))
        ttk.Button(d, text='Close', command=d.destroy).pack(side='bottom')

    def browse_assets(self):
        d = filedialog.askdirectory(initialdir=self.assets_var.get() or os.getcwd(), title='Select assets folder')
        if d:
            self.assets_var.set(d)
            # refresh spawner list
            try:
                self.spawner.refresh()
            except Exception:
                pass

if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)
    app = PetToolApp()
    app.mainloop()
