def parse_svg_path(d_str):
    """
    Parses an SVG path string with one 'M' command followed by a series of 'C' commands
    into cubic Bézier segments.
    Returns a list of segments where each segment is a tuple: (P0, P1, P2, P3).
    """
    tokens = d_str.strip().split()
    segments = []
    i = 0
    current_point = None

    # The path should start with an 'M' command
    if tokens[i] == 'M':
        coords = tokens[i + 1].split(',')
        current_point = (float(coords[0]), float(coords[1]))
        i += 2

    # Process subsequent "C" commands
    while i < len(tokens):
        if tokens[i] == 'C':
            control1 = tuple(map(float, tokens[i + 1].split(',')))
            control2 = tuple(map(float, tokens[i + 2].split(',')))
            endpoint = tuple(map(float, tokens[i + 3].split(',')))
            segments.append((current_point, control1, control2, endpoint))
            current_point = endpoint
            i += 4
        else:
            i += 1

    return segments

def cubic_bezier(P0, P1, P2, P3, t):
    """Computes a point on a cubic Bézier curve for parameter t (0 <= t <= 1)."""
    one_minus_t = 1 - t
    x = (one_minus_t**3)*P0[0] + 3*(one_minus_t**2)*t*P1[0] + 3*one_minus_t*(t**2)*P2[0] + (t**3)*P3[0]
    y = (one_minus_t**3)*P0[1] + 3*(one_minus_t**2)*t*P1[1] + 3*one_minus_t*(t**2)*P2[1] + (t**3)*P3[1]
    return (x, y)

def sample_curve(segments, samples_per_segment=100):
    """Samples points along all Bézier segments and returns a list of (x, y) points."""
    points = []
    for seg in segments:
        P0, P1, P2, P3 = seg
        for i in range(samples_per_segment):
            t = i / (samples_per_segment - 1)
            points.append(cubic_bezier(P0, P1, P2, P3, t))
    return points

def find_local_minima(points):
    """
    Uses finite differences to approximate the derivative and returns points where
    the derivative changes from negative to positive (local minima in y).
    """
    minima = []
    for i in range(1, len(points) - 1):
        x_prev, y_prev = points[i - 1]
        x_curr, y_curr = points[i]
        x_next, y_next = points[i + 1]
        
        # Avoid division by zero:
        if (x_curr - x_prev) == 0 or (x_next - x_curr) == 0:
            continue
        
        dydx_prev = (y_curr - y_prev) / (x_curr - x_prev)
        dydx_next = (y_next - y_curr) / (x_next - x_curr)
        
        # Local minimum in y: derivative changes from negative to positive
        if dydx_prev < 0 and dydx_next > 0:
            minima.append((x_curr, y_curr))
    return minima

def seconds_to_mmss(seconds):
    """Converts seconds to a mm:ss string."""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"

def get_timestamps(svg_string, video_dur_in_secs,percent_close_to_max=0):
    # Ask for the total video duration in seconds.
    total_duration = video_dur_in_secs

    # The complete SVG path string (one complete string)
    svg_path_str = svg_string
    # Parse the SVG path into cubic Bézier segments
    segments = parse_svg_path(svg_path_str)
    
    # Sample the entire curve with sufficient resolution
    points = sample_curve(segments, samples_per_segment=200)
    
    # Find local minima (interpreted as peaks in replay intensity)
    minima = find_local_minima(points)
    
    if not minima:
        print("No local minima (peak points) found.")
        return

    # Calculate intensities for each minimum (replay intensity = 100 - y)
    peak_points = [(x, y, 100 - y) for x, y in minima] #ALL THE PEAK POINTS
    max_intensity = max(peak_points, key=lambda p: p[2])[2]
    # Filter peaks to only keep those that are close to the maximum intensity (e.g., within 90%)

    threshold = percent_close_to_max * max_intensity  #######################IMP####################
    significant_peaks = [pt for pt in peak_points if pt[2] >= threshold]

    print("Significant replay peaks (timestamp in mm:ss, intensity):")
    for x, y, intensity in significant_peaks:
        timestamp_seconds = (x / 1000) * total_duration
        print(f"{seconds_to_mmss(timestamp_seconds)} -> Intensity: {intensity:.2f}")

    heat_map_info = []
    for x, y, intensity in significant_peaks:
            timestamp_seconds = (x / 1000) * total_duration
            heat_map_info.append({
                "time_in_sec": int(timestamp_seconds),
                "intensity": intensity
            })
    heat_map_info.sort(key=lambda item: item['intensity'], reverse=True)
    return {"heat_map_info": heat_map_info}
    # return significant_peaks
