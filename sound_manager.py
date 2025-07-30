import pygame
import numpy as np
import math

class SoundManager:
    def __init__(self, sample_rate=22050):
        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        self.sample_rate = sample_rate
        self.sounds = {}
        self.enabled = True
        
        # Generate procedural sounds
        self.generate_sounds()
    
    def generate_tone(self, frequency, duration, volume=0.3, fade_out=True):
        """Generate a simple tone"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            time = float(i) / self.sample_rate
            
            # Generate sine wave
            wave = volume * math.sin(frequency * 2 * math.pi * time)
            
            # Apply fade out
            if fade_out and i > frames * 0.7:
                fade_factor = 1.0 - (i - frames * 0.7) / (frames * 0.3)
                wave *= fade_factor
            
            arr[i] = [wave, wave]
        
        # Convert to pygame sound
        arr = np.array(arr * 32767, dtype=np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_noise(self, duration, volume=0.2, filter_freq=1000):
        """Generate filtered noise"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # White noise
            noise = (np.random.random() - 0.5) * volume
            
            # Simple low-pass filter effect
            if i > 0:
                noise = 0.7 * noise + 0.3 * arr[i-1][0]
            
            # Fade out
            if i > frames * 0.5:
                fade_factor = 1.0 - (i - frames * 0.5) / (frames * 0.5)
                noise *= fade_factor
            
            arr[i] = [noise, noise]
        
        arr = np.array(arr * 32767, dtype=np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_sweep(self, start_freq, end_freq, duration, volume=0.3):
        """Generate a frequency sweep"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            time = float(i) / self.sample_rate
            progress = float(i) / frames
            
            # Interpolate frequency
            freq = start_freq + (end_freq - start_freq) * progress
            
            # Generate wave
            wave = volume * math.sin(freq * 2 * math.pi * time)
            
            # Envelope
            envelope = math.sin(math.pi * progress)
            wave *= envelope
            
            arr[i] = [wave, wave]
        
        arr = np.array(arr * 32767, dtype=np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_chord(self, frequencies, duration, volume=0.2):
        """Generate a chord from multiple frequencies"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            time = float(i) / self.sample_rate
            wave = 0
            
            # Sum all frequencies
            for freq in frequencies:
                wave += volume * math.sin(freq * 2 * math.pi * time) / len(frequencies)
            
            # Envelope
            envelope = 1.0
            if i < frames * 0.1:  # Attack
                envelope = float(i) / (frames * 0.1)
            elif i > frames * 0.8:  # Release
                envelope = 1.0 - (i - frames * 0.8) / (frames * 0.2)
            
            wave *= envelope
            arr[i] = [wave, wave]
        
        arr = np.array(arr * 32767, dtype=np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_sounds(self):
        """Generate all game sounds"""
        try:
            # Food eating sound - pleasant chord
            self.sounds['eat'] = self.generate_chord([440, 554, 659], 0.2, 0.3)
            
            # Power-up sound - ascending sweep
            self.sounds['powerup'] = self.generate_sweep(220, 880, 0.5, 0.4)
            
            # Collision sound - noise burst
            self.sounds['collision'] = self.generate_noise(0.3, 0.3)
            
            # Speed boost sound - quick ascending tones
            self.sounds['speed'] = self.generate_sweep(440, 1760, 0.3, 0.3)
            
            # Invincibility sound - magical chord
            self.sounds['invincible'] = self.generate_chord([523, 659, 784, 1047], 0.4, 0.25)
            
            # Growth boost sound - deep rumble
            self.sounds['growth'] = self.generate_tone(110, 0.4, 0.4)
            
            # Double points sound - coin-like
            self.sounds['double'] = self.generate_chord([880, 1108], 0.3, 0.3)
            
            # Slow opponent sound - descending sweep
            self.sounds['slow'] = self.generate_sweep(440, 220, 0.4, 0.3)
            
        except Exception as e:
            print(f"Warning: Could not generate sounds: {e}")
            self.enabled = False
    
    def play(self, sound_name, volume=1.0):
        """Play a sound effect"""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            print(f"Warning: Could not play sound {sound_name}: {e}")
    
    def set_enabled(self, enabled):
        """Enable or disable sound effects"""
        self.enabled = enabled
        if not enabled:
            pygame.mixer.stop()
    
    def cleanup(self):
        """Clean up sound resources"""
        pygame.mixer.quit()