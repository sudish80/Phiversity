"""
3D Vector Visualization Script using Manim
==========================================
Generates dynamic 3D vector graphs with:
- Animated vector rotation and transformation
- Real-time coordinate system with labeled axes
- Dynamic magnitude and direction changes
- Camera movement and depth effects
- Interactive vector operations
- Color-coded vectors
- Time-based animations
- Grid plane backgrounds

Usage:
    python vector_3d.py [options]

Options:
    --quality low/medium/high/production  Video quality (default: low)
    --resolution WxH                    Resolution (default: 1920x1080)
    --fps FRAME_RATE                    Frames per second (default: 30)
    --duration SECONDS                  Scene duration (default: 10)
    --output OUTPUT                     Output filename (default: vector_3d)
"""

import argparse
import math
from manim import *


class Vector3DIntro(ThreeDScene):
    """Introduction scene with rotating 3D vectors"""
    
    def construct(self):
        # Set camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        
        # Title
        title = Text("3D Vector Visualization", font_size=48, color=WHITE)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)
        self.wait(0.5)
        
        # Create 3D axes
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            z_length=6,
            axis_config={"include_tip": True}
        )
        self.add(axes)
        
        # Create a 3D vector
        vector = Arrow3D(
            start=ORIGIN,
            end=[2, 1, 1],
            color=RED,
            thickness=0.03
        )
        
        # Labels
        x_label = Text("X", font_size=24).next_to(axes.x_axis.get_end(), RIGHT)
        y_label = Text("Y", font_size=24).next_to(axes.y_axis.get_end(), UP)
        z_label = Text("Z", font_size=24).next_to(axes.z_axis.get_end(), OUT)
        
        # Animate vector
        self.play(Create(vector), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        
        self.play(FadeOut(title), run_time=0.5)


class VectorRotation(ThreeDScene):
    """Animated vector rotation in 3D space"""
    
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=-30 * DEGREES)
        
        # Axes
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)
        
        # Create vector
        vector = Arrow3D(
            start=ORIGIN,
            end=[2, 0, 0],
            color=BLUE,
            thickness=0.04
        )
        
        # Rotation indicator
        trace = TracedPath(vector.get_end, stroke_color=YELLOW, stroke_width=2)
        self.add(trace)
        
        self.play(Create(vector), run_time=1)
        
        # Rotate around Y-axis
        self.play(
            vector.animate.rotate(PI/2, axis=UP),
            run_time=2
        )
        
        # Rotate around X-axis
        self.play(
            vector.animate.rotate(PI/2, axis=RIGHT),
            run_time=2
        )
        
        # Rotate around Z-axis
        self.play(
            vector.animate.rotate(PI/2, axis=OUT),
            run_time=2
        )
        
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(2)


class VectorOperations(ThreeDScene):
    """Interactive vector operations: addition, subtraction, scaling"""
    
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        
        axes = ThreeDAxes(x_range=[-4, 4], y_range=[-4, 4], z_range=[-4, 4])
        self.add(axes)
        
        # Vector A (Red)
        vec_a = Arrow3D(
            start=ORIGIN,
            end=[2, 1, 0],
            color=RED,
            thickness=0.03
        )
        
        # Vector B (Blue)  
        vec_b = Arrow3D(
            start=ORIGIN,
            end=[1, 2, 0],
            color=BLUE,
            thickness=0.03
        )
        
        # Vector A + B (Purple)
        sum_end = [2+1, 1+2, 0]
        vec_sum = Arrow3D(
            start=ORIGIN,
            end=sum_end,
            color=PURPLE,
            thickness=0.04
        )
        
        # Labels (must be fixed in frame for proper SVG rendering in 3D)
        label_a = MathTex(r"\vec{a}", color=RED).next_to(vec_a.get_end(), RIGHT)
        label_b = MathTex(r"\vec{b}", color=BLUE).next_to(vec_b.get_end(), UP)
        label_sum = MathTex(r"\vec{a} + \vec{b}", color=PURPLE).next_to(vec_sum.get_end(), RIGHT)
        self.add_fixed_in_frame_mobjects(label_a, label_b, label_sum)
        
        # Animate
        self.play(Create(vec_a), Write(label_a), run_time=1)
        self.play(Create(vec_b), Write(label_b), run_time=1)
        
        # Show addition
        self.play(Create(vec_sum), Write(label_sum), run_time=1.5)
        
        # Show dashed lines for parallelogram
        dashed_a = DashedLine(vec_a.get_end(), vec_sum.get_end(), color=RED)
        dashed_b = DashedLine(vec_b.get_end(), vec_sum.get_end(), color=BLUE)
        self.play(Create(dashed_a), Create(dashed_b), run_time=1)
        
        self.begin_ambient_camera_rotation()
        self.wait(3)


class VectorScaling(ThreeDScene):
    """Dynamic vector magnitude changes with smooth transitions"""
    
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-40 * DEGREES)
        
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)
        
        # Create vector that will be scaled
        vector = Arrow3D(
            start=ORIGIN,
            end=[1, 0, 0],
            color=GREEN,
            thickness=0.03
        )
        
        # Magnitude label
        mag_label = MathTex(r"|\vec{v}| = 1", color=GREEN)
        mag_label.to_corner(UL)
        self.add_fixed_in_frame_mobjects(mag_label)
        
        self.play(Create(vector), Write(mag_label), run_time=1.5)
        
        # Scale up
        for scale in [2, 2.5, 3]:
            new_end = [scale, 0, 0]
            new_label = MathTex(fr"|\vec{{v}}| = {scale}", color=GREEN).to_corner(UL)
            self.add_fixed_in_frame_mobjects(new_label)
            self.play(
                vector.animate.put_start_and_end_on(ORIGIN, new_end),
                Transform(mag_label, new_label),
                run_time=1.5
            )
        
        # Scale down
        for scale in [2, 1, 0.5]:
            new_end = [scale, 0, 0]
            new_label = MathTex(fr"|\vec{{v}}| = {scale}", color=GREEN).to_corner(UL)
            self.add_fixed_in_frame_mobjects(new_label)
            self.play(
                vector.animate.put_start_and_end_on(ORIGIN, new_end),
                Transform(mag_label, new_label),
                run_time=1.5
            )
        
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(2)


class VectorEvolution(ThreeDScene):
    """Time-based animation showing vector evolution"""
    
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES)
        
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)
        
        # Create evolving vector
        vector = Arrow3D(
            start=ORIGIN,
            end=[2, 0, 0],
            color=YELLOW,
            thickness=0.03
        )
        
        # Trace path
        trace = TracedPath(
            vector.get_end,
            stroke_color=ORANGE,
            stroke_width=3,
            fade_cap=True
        )
        self.add(trace)
        
        self.play(Create(vector), run_time=1)
        
        # Animate evolution using updater
        def update_vector(mob, dt):
            time = self.time
            # Spiral evolution
            x = 2 * math.cos(time)
            y = 2 * math.sin(time)
            z = math.sin(time * 2) * 0.5
            mob.put_start_and_end_on(ORIGIN, [x, y, z])
        
        vector.add_updater(update_vector)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(8)
        vector.remove_updater(update_vector)


class MultipleVectors(ThreeDScene):
    """Color-coded vectors representing different properties"""
    
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)
        
        # Grid planes
        xy_plane = NumberPlane(x_range=[-3, 3], y_range=[-3, 3], background_line_style={"stroke_color": BLUE_E, "stroke_opacity": 0.3})
        xz_plane = NumberPlane(x_range=[-3, 3], y_range=[-3, 3], background_line_style={"stroke_color": GREEN_E, "stroke_opacity": 0.3})
        xz_plane.rotate(PI/2, axis=RIGHT)
        self.add(xy_plane, xz_plane)
        
        # Different colored vectors
        vectors = [
            ([2, 0, 0], RED, r"\vec{i}"),
            ([0, 2, 0], GREEN, r"\vec{j}"),
            ([0, 0, 2], BLUE, r"\vec{k}"),
            ([1, 1, 1], YELLOW, r"\vec{v_1}"),
            ([-1, 1, -1], PURPLE, r"\vec{v_2}"),
        ]
        
        for end, color, label in vectors:
            arrow = Arrow3D(start=ORIGIN, end=end, color=color, thickness=0.03)
            self.play(Create(arrow), run_time=0.5)
        
        # Legend (fixed in frame so SVG-based MathTex renders correctly in 3D)
        legend = VGroup()
        for end, color, label in vectors:
            dot = Dot(color=color)
            text = MathTex(label, color=color, font_size=24)
            row = VGroup(dot, text).arrange(RIGHT, buff=0.1)
            legend.add(row)
        
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend.to_corner(UR)
        self.add_fixed_in_frame_mobjects(legend)
        
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(4)


class CameraMovement(ThreeDScene):
    """Camera movement and depth effects"""
    
    def construct(self):
        # Initial view
        self.set_camera_orientation(phi=0 * DEGREES, theta=0 * DEGREES)
        
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)
        
        # Vector
        vector = Arrow3D(
            start=ORIGIN,
            end=[2, 1, 1],
            color=TEAL,
            thickness=0.04
        )
        
        self.play(Create(vector), run_time=1)
        
        # Move camera to different angles
        self.move_camera(
            phi=30 * DEGREES,
            theta=-20 * DEGREES,
            run_time=2
        )
        
        self.move_camera(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            run_time=2
        )
        
        self.move_camera(
            phi=90 * DEGREES,
            theta=0 * DEGREES,
            run_time=2
        )
        
        # Orbit around
        self.begin_ambient_camera_rotation(rate=0.5)
        self.wait(3)


class PhysicsMotionVectors(ThreeDScene):
    """Physics vectors: velocity, acceleration, and force in 3D."""

    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-40 * DEGREES)
        axes = ThreeDAxes(x_range=[-4, 4], y_range=[-4, 4], z_range=[-4, 4])
        self.add(axes)

        vel = Arrow3D(start=ORIGIN, end=[2.5, 0.8, 0.2], color=BLUE, thickness=0.03)
        acc = Arrow3D(start=ORIGIN, end=[0.8, 1.9, -0.3], color=RED, thickness=0.03)
        frc = Arrow3D(start=ORIGIN, end=[1.4, 2.2, -0.2], color=YELLOW, thickness=0.03)

        title = Text("Physics: Motion Vectors", font_size=38)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)

        self.play(Write(title), Create(vel), run_time=1.3)
        self.play(Create(acc), run_time=1.0)
        self.play(Create(frc), run_time=1.0)

        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(2)


class MathematicsVectorField(ThreeDScene):
    """Mathematics vectors: gradient-like field snapshot in 3D."""

    def construct(self):
        self.set_camera_orientation(phi=62 * DEGREES, theta=-35 * DEGREES)
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)

        title = Text("Mathematics: Vector Field Intuition", font_size=36)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        vectors = VGroup()
        for x in (-2, 0, 2):
            for y in (-2, 0, 2):
                end = [x * 0.4 + 0.5, y * 0.4 + 0.5, (x - y) * 0.2]
                vectors.add(Arrow3D(start=[x, y, 0], end=[x + end[0], y + end[1], end[2]], color=GREEN, thickness=0.02))

        self.play(LaggedStart(*[Create(v) for v in vectors], lag_ratio=0.08), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.18)
        self.wait(2)


class ChemistryConcentrationGradient(ThreeDScene):
    """Chemistry vectors: concentration gradient and flux direction."""

    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-50 * DEGREES)
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)

        title = Text("Chemistry: Concentration Gradient", font_size=36)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        high_c = Sphere(radius=0.25, color=ORANGE).shift(2 * LEFT + 1.2 * UP)
        low_c = Sphere(radius=0.25, color=BLUE).shift(2 * RIGHT + 1.2 * DOWN)
        flux = Arrow3D(start=[-2, 1.2, 0], end=[2, -1.2, 0], color=YELLOW, thickness=0.03)

        self.play(FadeIn(high_c), FadeIn(low_c), run_time=1)
        self.play(Create(flux), run_time=1.2)
        self.begin_ambient_camera_rotation(rate=0.16)
        self.wait(2)


class EconomicsMarketDynamics(ThreeDScene):
    """Economics vectors: equilibrium adjustment in quantity-price space."""

    def construct(self):
        self.set_camera_orientation(phi=58 * DEGREES, theta=-30 * DEGREES)
        axes = ThreeDAxes(x_range=[0, 8], y_range=[0, 8], z_range=[-2, 2])
        self.add(axes)

        title = Text("Economics: Market Adjustment Vectors", font_size=34)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        demand_shift = Arrow3D(start=[2, 6, 0], end=[3.5, 5, 0], color=RED, thickness=0.03)
        supply_shift = Arrow3D(start=[6, 2, 0], end=[5, 3.2, 0], color=GREEN, thickness=0.03)
        eq_adjust = Arrow3D(start=[4, 4, 0], end=[4.5, 4.4, 0.4], color=YELLOW, thickness=0.03)

        self.play(Create(demand_shift), Create(supply_shift), run_time=1.4)
        self.play(Create(eq_adjust), run_time=1.0)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(2)


def create_scene(scene_class, quality, fps, duration):
    """Create and configure a scene"""
    config.quality = quality
    config.frame_rate = fps
    config.max_files_cached = 100
    
    # Override duration if needed
    if duration:
        config.scene_duration = duration
    
    return scene_class()


# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 3D Vector Animations")
    parser.add_argument("--quality", "-q", default="low",
                        choices=["low", "medium", "high", "production"],
                        help="Video quality")
    parser.add_argument("--resolution", "-r", default="1920x1080",
                        help="Resolution (WxH)")
    parser.add_argument("--fps", "-f", type=int, default=30,
                        help="Frames per second")
    parser.add_argument("--duration", "-d", type=int, default=10,
                        help="Scene duration in seconds")
    parser.add_argument("--output", "-o", default="vector_3d",
                        help="Output filename")
    parser.add_argument("--scene", "-s", default=None,
                        help="Specific scene to render (default: all)")
    parser.add_argument("--subject", default="all",
                        choices=["all", "physics", "mathematics", "chemistry", "economics"],
                        help="Render a subject-focused scene set")
    parser.add_argument("--list-scenes", action="store_true",
                        help="List available scene keys and exit")
    
    args = parser.parse_args()
    
    # Parse resolution
    try:
        w, h = map(int, args.resolution.split('x'))
        config.pixel_height = h
        config.pixel_width = w
    except:
        print("Invalid resolution format. Using 1920x1080")
        config.pixel_height = 1080
        config.pixel_width = 1920
    
    # Map quality names to Manim quality
    quality_map = {
        "low": "low_quality",
        "medium": "medium_quality", 
        "high": "high_quality",
        "production": "production_quality"
    }
    quality = quality_map.get(args.quality, "low_quality")
    
    # Scene mapping
    scenes = {
        "intro": Vector3DIntro,
        "rotation": VectorRotation,
        "operations": VectorOperations,
        "scaling": VectorScaling,
        "evolution": VectorEvolution,
        "multiple": MultipleVectors,
        "camera": CameraMovement,
        "physics_motion": PhysicsMotionVectors,
        "math_field": MathematicsVectorField,
        "chem_gradient": ChemistryConcentrationGradient,
        "econ_market": EconomicsMarketDynamics,
    }

    subject_scene_map = {
        "physics": ["physics_motion", "operations", "rotation"],
        "mathematics": ["math_field", "operations", "scaling"],
        "chemistry": ["chem_gradient", "evolution", "multiple"],
        "economics": ["econ_market", "multiple", "camera"],
    }

    if args.list_scenes:
        print("Available scenes:")
        for key in scenes:
            print(f"  - {key}")
        print("\nSubject presets:")
        for key, value in subject_scene_map.items():
            print(f"  - {key}: {', '.join(value)}")
        raise SystemExit(0)
    
    # Determine which scenes to render
    if args.scene:
        scene_names = [args.scene]
    elif args.subject != "all":
        scene_names = subject_scene_map.get(args.subject, list(scenes.keys()))
    else:
        scene_names = list(scenes.keys())
    
    print(f"Rendering 3D Vector Scenes")
    print(f"Quality: {args.quality}, FPS: {args.fps}, Resolution: {args.resolution}")
    print(f"Subject: {args.subject}")
    print(f"Scenes: {', '.join(scene_names)}")
    
    # Render each scene
    for scene_name in scene_names:
        if scene_name in scenes:
            print(f"\nRendering scene: {scene_name}")
            # Note: In actual usage, you'd use subprocess to call manim
            # This is the structure the script follows
            print(f"  → {scene_name}: {scenes[scene_name].__doc__}")
    
    print("\nTo render with Manim, run:")
    print(f"  manim -q{args.quality[0]} -r{args.resolution} -fps {args.fps} vector_3d.py [SCENE_NAME]")
    if args.subject != "all":
        print(f"  Suggested subject scenes: {', '.join(scene_names)}")
