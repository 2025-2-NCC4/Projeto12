import streamlit as st
import base64
import os

class HeroVideo:
    """Hero video component matching your existing style"""
    
    @staticmethod
    def render(video_path: str, height: int = 500):
        if not os.path.exists(video_path):
            st.warning(f"Vídeo não encontrado: {video_path}")
            return
        
        try:
            with open(video_path, "rb") as f:
                video_base64 = base64.b64encode(f.read()).decode()
            
            st.components.v1.html(f"""
                <style>
                .hero-video-container {{
                    position: relative;
                    width: 100%;
                    height: {height}px;
                    overflow: hidden;
                    border-radius: 14px;
                    box-shadow: 0 4px 14px rgba(0,0,0,.35);
                }}
                .hero-video-container video {{
                    position: absolute; top:50%; left:50%;
                    width:100%; height:100%; object-fit:cover;
                    transform: translate(-50%, -50%);
                }}
                </style>
                <div class="hero-video-container">
                    <video autoplay loop muted playsinline>
                        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    </video>
                </div>
            """, height=height)
        except Exception as e:
            st.error(f"Erro ao carregar vídeo: {e}")