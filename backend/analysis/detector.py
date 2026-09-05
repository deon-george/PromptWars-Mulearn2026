import os
import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class FaceDetection:
    x: int
    y: int
    width: int
    height: int
    confidence: float
    region_label: str = "face"


@dataclass
class ArtifactFinding:
    name: str
    score: float
    detail: str


@dataclass
class AnalysisResult:
    media_type: str
    anomaly_score: float
    face_detections: List[Dict[str, Any]] = field(default_factory=list)
    artifact_findings: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    heatmap: Optional[List[List[float]]] = None
    processing_notes: List[str] = field(default_factory=list)


class FaceLocalizer:
    """Lightweight face localization using OpenCV DNN face detector or Haar cascade fallback."""
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), 'models')
        self.prototxt = os.path.join(self.model_dir, 'deploy.prototxt')
        self.weights = os.path.join(self.model_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
        self._net = None
        self._cascade = None
        self._use_dnn = False
    
    def _ensure_dnn_model(self):
        if self._net is not None:
            return self._net
        if not os.path.exists(self.prototxt) or not os.path.exists(self.weights):
            return None
        try:
            if not hasattr(cv2.dnn, 'readNetFromCaffe'):
                return None
            self._net = cv2.dnn.readNetFromCaffe(self.prototxt, self.weights)
            return self._net
        except Exception:
            return None
    
    def _ensure_cascade(self):
        if self._cascade is not None:
            return self._cascade
        cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        if not os.path.exists(cascade_path):
            return None
        self._cascade = cv2.CascadeClassifier(cascade_path)
        return self._cascade
    
    def detect(self, image_bgr) -> List[FaceDetection]:
        # Try DNN first
        net = self._ensure_dnn_model()
        if net is not None:
            try:
                h, w = image_bgr.shape[:2]
                blob = cv2.dnn.blobFromImage(image_bgr, 1.0, (300, 300), (104.0, 177.0, 123.0), False, False)
                net.setInput(blob)
                detections = net.forward()
                results: List[FaceDetection] = []
                for i in range(detections.shape[2]):
                    confidence = float(detections[0, 0, i, 2])
                    if confidence < 0.5:
                        continue
                    x1 = int(detections[0, 0, i, 3] * w)
                    y1 = int(detections[0, 0, i, 4] * h)
                    x2 = int(detections[0, 0, i, 5] * w)
                    y2 = int(detections[0, 0, i, 6] * h)
                    box_w = max(1, x2 - x1)
                    box_h = max(1, y2 - y1)
                    results.append(FaceDetection(
                        x=max(0, x1),
                        y=max(0, y1),
                        width=min(w - x1, box_w),
                        height=min(h - y1, box_h),
                        confidence=confidence,
                    ))
                if results:
                    self._use_dnn = True
                    return results
            except Exception:
                pass
        
        # Fallback to Haar cascade
        cascade = self._ensure_cascade()
        if cascade is None:
            return []
        
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        results = []
        for (x, y, w, h) in faces:
            results.append(FaceDetection(
                x=int(x), y=int(y), width=int(w), height=int(h),
                confidence=0.8,
            ))
        return results


class ImageAnomalyAnalyzer:
    """Image anomaly detection with face localization and artifact analysis."""
    
    def __init__(self, face_localizer: Optional[FaceLocalizer] = None):
        self.face_localizer = face_localizer or FaceLocalizer()
    
    def analyze(self, path: str) -> AnalysisResult:
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError('Unreadable image file')
        
        findings: List[ArtifactFinding] = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        faces = self.face_localizer.detect(image)
        face_regions = []
        if faces:
            face_regions = [
                {'x': f.x, 'y': f.y, 'width': f.width, 'height': f.height, 'confidence': round(f.confidence, 3)}
                for f in faces
            ]
            findings.append(ArtifactFinding(
                name='face_detection',
                score=min(1.0, len(faces) / 5.0),
                detail=f"Detected {len(faces)} face region(s)."
            ))
        
        cell_h = max(1, h // 8)
        cell_w = max(1, w // 8)
        heatmap = []
        laplacian_vals = []
        for y in range(0, h, cell_h):
            row = []
            for x in range(0, w, cell_w):
                y2 = min(h, y + cell_h)
                x2 = min(w, x + cell_w)
                cell = gray[y:y2, x:x2]
                lap = float(cv2.Laplacian(cell, cv2.CV_64F).var())
                row.append(lap)
                laplacian_vals.append(lap)
            heatmap.append(row)
        
        flat = laplacian_vals
        min_v, max_v = min(flat), max(flat)
        denom = max_v - min_v if max_v != min_v else 1.0
        heatmap = [[max(0.0, min(1.0, (v - min_v) / denom)) for v in row] for row in heatmap]
        
        low_var_ratio = sum(1 for v in flat if v < (min_v + 0.25 * denom)) / max(len(flat), 1)
        edge_score = float(np.mean(flat) / max_v)
        
        findings.append(ArtifactFinding(name='low_texture_ratio', score=float(low_var_ratio), detail='Low-variance texture regions.'))
        findings.append(ArtifactFinding(name='edge_consistency', score=edge_score, detail='Edge inconsistency metric.'))
        
        anomaly_score = float(np.clip(0.35 * low_var_ratio + 0.35 * (1 - edge_score) + 0.3 * (len(faces) > 0), 0, 1))
        
        notes = ['OpenCV DNN face detection used; lightweight feature extraction only.']
        if not getattr(self.face_localizer, '_use_dnn', False):
            notes.append('DNN face detector unavailable; Haar cascade fallback used.')
        
        return AnalysisResult(
            media_type='image',
            anomaly_score=anomaly_score,
            face_detections=face_regions,
            artifact_findings=[{'name': f.name, 'score': f.score, 'detail': f.detail} for f in findings],
            heatmap=heatmap,
            metadata={'width': int(w), 'height': int(h), 'faces': len(faces)},
            processing_notes=notes
        )


class AudioAnomalyAnalyzer:
    """Audio anomaly detection using spectral features."""
    
    def analyze(self, path: str) -> AnalysisResult:
        import librosa
        y, sr = librosa.load(path, sr=None, mono=True)
        flatness = float(np.mean(librosa.feature.spectral_flatness(y=y, sr=sr)))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=y, frame_length=1024, hop_length=512)))
        cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
        
        flatness_norm = min(1.0, flatness * 3.0)
        zcr_norm = min(1.0, zcr * 10.0)
        
        findings = [
            ArtifactFinding(name='spectral_flatness', score=flatness_norm, detail='Spectral flatness indicator.'),
            ArtifactFinding(name='zero_crossing_rate', score=zcr_norm, detail='Zero crossing variance.'),
            ArtifactFinding(name='spectral_centroid', score=float(cent / 4000.0), detail='Spectral centroid feature.'),
        ]
        
        anomaly_score = float(np.clip(0.4 * flatness_norm + 0.3 * zcr_norm + 0.3 * min(1.0, cent / 4000.0), 0, 1))
        return AnalysisResult(
            media_type='audio',
            anomaly_score=anomaly_score,
            artifact_findings=[{'name': f.name, 'score': f.score, 'detail': f.detail} for f in findings],
            metadata={'duration_seconds': float(librosa.get_duration(y=y, sr=sr)), 'sample_rate': int(sr)}
        )


class VideoAnomalyAnalyzer:
    """Video anomaly detection via sampled frame analysis."""
    
    def analyze(self, path: str) -> AnalysisResult:
        image_analyzer = ImageAnomalyAnalyzer()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError('Unreadable video file')
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = 0
        sampled = 0
        anomaly_scores = []
        all_findings = []
        all_faces = []
        
        while True:
            ret, frame = cap.read()
            if not ret or sampled > 60:
                break
            frame_count += 1
            if frame_count % max(1, int(fps // 4)) != 0:
                continue
            sampled += 1
            tmp_path = os.path.join(os.path.dirname(__file__), f'_frame_{sampled}.jpg')
            cv2.imwrite(tmp_path, frame)
            try:
                res = image_analyzer.analyze(tmp_path)
                anomaly_scores.append(res.anomaly_score)
                all_findings.extend(res.artifact_findings)
                all_faces.extend(res.face_detections)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        cap.release()
        if not anomaly_scores:
            raise ValueError('Video has no decodable frames')
        
        anomaly_score = float(np.clip(float(np.mean(anomaly_scores)), 0, 1))
        return AnalysisResult(
            media_type='video',
            anomaly_score=anomaly_score,
            face_detections=all_faces,
            artifact_findings=all_findings,
            metadata={'frames_sampled': sampled, 'fps': float(fps)}
        )


def analyze(path: str, media_type: str) -> AnalysisResult:
    if media_type == 'image':
        return ImageAnomalyAnalyzer().analyze(path)
    if media_type == 'audio':
        return AudioAnomalyAnalyzer().analyze(path)
    if media_type == 'video':
        return VideoAnomalyAnalyzer().analyze(path)
    raise ValueError(f'Unsupported media type: {media_type}')
