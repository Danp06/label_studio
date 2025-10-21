"""
Gestor de Vistas para Label Studio
Clase reutilizable para configurar vistas de proyectos
"""

from typing import List, Optional, Dict
from label_studio_sdk import LabelStudio


class LabelStudioViewManager:
    """
    Clase para gestionar vistas de Label Studio de manera reutilizable.
    El orden de las columnas en la lista determina cómo aparecen en la vista.
    """
    
    # Lista completa de todas las columnas estándar disponibles en Label Studio
    COLUMNAS_ESTANDAR = [
        'tasks:id',
        'tasks:inner_id',
        'tasks:completed_at',
        'tasks:cancelled_annotations',
        'tasks:total_annotations',
        'tasks:total_predictions',
        'tasks:annotators',
        'tasks:annotations_results',
        'tasks:annotations_ids',
        'tasks:predictions_score',
        'tasks:predictions_model_versions',
        'tasks:predictions_results',
        'tasks:file_upload',
        'tasks:storage_filename',
        'tasks:created_at',
        'tasks:updated_at',
        'tasks:updated_by',
        'tasks:avg_lead_time',
        'tasks:draft_exists',
        'tasks:agreement',
        'tasks:comments',
        'tasks:ground_truth',
        'tasks:reviewed',
        'tasks:reviewers',
        'tasks:reviews_accepted',
        'tasks:reviews_rejected',
        'tasks:unresolved_comment_count'
    ]
    
    def __init__(self, client: LabelStudio):
        """
        Inicializa el gestor de vistas.
        
        Args:
            client: Instancia del cliente de Label Studio
        """
        self.client = client
    
    def obtener_vista_default(self, project_id: int):
        """
        Obtiene la vista por defecto de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            La vista por defecto o None si no existe
        """
        try:
            views = self.client.views.list(project=project_id)
            if views and len(views) > 0:
                # La primera vista suele ser la default
                return views[0]
            return None
        except Exception as e:
            print(f"⚠️ Error obteniendo vistas del proyecto {project_id}: {e}")
            return None
    
    def detectar_columnas_custom(self, project_id: int) -> List[str]:
        """
        Detecta las columnas personalizadas de un proyecto basándose en la primera tarea.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de nombres de columnas custom con prefijo 'tasks:data.'
        """
        try:
            tasks = self.client.tasks.list(project=project_id, page_size=1)
            if tasks and len(tasks) > 0:
                primera_tarea = tasks[0]
                if hasattr(primera_tarea, 'data') and isinstance(primera_tarea.data, dict):
                    campos_custom = [f'tasks:data.{key}' for key in primera_tarea.data.keys()]
                    print(f"  📋 Columnas personalizadas detectadas: {len(campos_custom)}")
                    return campos_custom
        except Exception as e:
            print(f"  ⚠️ No se pudieron detectar columnas personalizadas: {e}")
        
        return []
    
    def configurar_vista(
        self,
        project_id: int,
        columnas_visibles: List[str],
        view_id: Optional[int] = None,
        auto_detectar_custom: bool = True
    ):
        """
        Configura una vista de Label Studio con columnas específicas.
        Las columnas aparecerán en el ORDEN especificado en la lista.
        
        Args:
            project_id: ID del proyecto
            columnas_visibles: Lista de columnas que quieres ver EN EL ORDEN DESEADO
                              Puede usar nombres cortos para campos custom (ej: 'sentence')
                              o nombres completos (ej: 'tasks:data.sentence')
            view_id: ID de la vista a actualizar (si es None, usa la vista default)
            auto_detectar_custom: Si es True, detecta automáticamente columnas custom del proyecto
        
        Returns:
            La vista actualizada o None si hay error
        """
        
        # Si no se especifica view_id, obtener la vista default
        if view_id is None:
            vista_default = self.obtener_vista_default(project_id)
            if vista_default is None:
                print(f"❌ No se pudo obtener la vista default del proyecto {project_id}")
                return None
            view_id = vista_default.id
            print(f"  📌 Usando vista default (ID: {view_id})")
        
        # Normalizar nombres de columnas (agregar prefijo tasks:data. si es necesario)
        columnas_normalizadas = []
        columnas_custom_detectadas = []
        
        if auto_detectar_custom:
            columnas_custom_detectadas = self.detectar_columnas_custom(project_id)
        
        for col in columnas_visibles:
            # Si ya tiene el prefijo completo, usarlo tal cual
            if col.startswith('tasks:'):
                columnas_normalizadas.append(col)
            else:
                # Asumir que es un campo custom y agregar el prefijo
                columnas_normalizadas.append(f'tasks:data.{col}')
        
        # Construir lista completa de columnas disponibles
        todas_las_columnas = self.COLUMNAS_ESTANDAR.copy()
        todas_las_columnas.extend(columnas_custom_detectadas)
        
        # Calcular las columnas que deben ocultarse
        columnas_ocultas = [col for col in todas_las_columnas if col not in columnas_normalizadas]
        
        # Construir el objeto de datos para la vista
        view_data = {
            "hiddenColumns": {
                "explore": columnas_ocultas,
                "labeling": columnas_ocultas
            },
            "columnsWidth": {},
            "columnsDisplayType": {}
        }
        
        try:
            # Actualizar la vista
            updated_view = self.client.views.update(
                id=str(view_id),
                data=view_data,
                project=project_id
            )
            
            print(f"  ✅ Vista configurada con {len(columnas_normalizadas)} columnas")
            print(f"  📊 Orden de columnas:")
            for i, col in enumerate(columnas_normalizadas, 1):
                # Mostrar nombre simplificado para mejor legibilidad
                nombre_simple = col.replace('tasks:data.', '').replace('tasks:', '')
                print(f"     {i}. {nombre_simple}")
            
            return updated_view
            
        except Exception as e:
            print(f"  ❌ Error actualizando la vista: {e}")
            return None
    
    def configurar_desde_config(
        self,
        project_id: int,
        config: Dict
    ):
        """
        Configura una vista desde un diccionario de configuración.
        Útil para leer desde JSON.
        
        Args:
            project_id: ID del proyecto
            config: Diccionario con la llave:
                   - columns: Lista de columnas visibles EN EL ORDEN DESEADO (requerido)
        
        Returns:
            La vista actualizada o None si hay error
        """
        
        if 'columns' not in config:
            print(f"  ⚠️ No se encontró la clave 'columns' en la configuración")
            return None
        
        return self.configurar_vista(
            project_id=project_id,
            columnas_visibles=config['columns'],
            view_id=config.get('view_id'),
            auto_detectar_custom=config.get('auto_detect_custom', True)
        )


# Ejemplo de uso básico
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client = LabelStudio(
        base_url=os.getenv('LABEL_STUDIO_URL'),
        api_key=os.getenv('LABEL_STUDIO_LEGACY_API_KEY')
    )
    
    # Crear instancia del gestor
    view_manager = LabelStudioViewManager(client)
    
    # Ejemplo: Las columnas aparecerán en este orden exacto
    print("\n" + "="*60)
    print("CONFIGURANDO VISTA")
    print("="*60)
    
    view_manager.configurar_vista(
        project_id=2,
        columnas_visibles=[
            'tasks:id',           # 1ra columna
            'sentence_id',        # 2da columna
            'sentence',           # 3ra columna
            'tasks:completed_at', # 4ta columna
            'tasks:total_annotations',  # 5ta columna
            'tasks:annotators'    # 6ta columna
        ]
    )
    
    print("\n✅ Las columnas aparecerán en el orden especificado en la lista!")