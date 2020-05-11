import os
import tensorflow as tf
import keras.backend as kb

class Metric:
    def __init__(self, name, step_name='training'):
        self.name = name
        self.step_name = step_name

class Plot:
    def __init__(self, name, metrics):
        self.name = name
        self.metrics = metrics

class MixedTensorBoard:
    def __init__(self, plots, log_dir):
        self.log_dir = log_dir

        steps = set()
        self.metrics = {}

        # Generates folder for all steps, this, in order to plot multiple colors
        for plot in plots:
            for metric in plot.metrics:
                steps.add(metric.step_name)
                self.metrics[metric.name] = plot.name

        #Generates writers for all steps
        self.writers = {step: tf.summary.FileWriter( os.path.join(log_dir, step) ) for step in steps }
       
    
    def add_checkpoint(self, history, step_name, global_step):

        for metric, value in history.items():

            if metric in self.metrics:
                if type(value[len(value) - 1]) is str:
                    summary = kb.get_session().run(tf.summary.text(name=self.metrics[metric], tensor=tf.convert_to_tensor(value[len(value) - 1])))

                    if step_name in self.writers:
                        self.writers[step_name].add_summary(summary, global_step)

                else:
                    summary = tf.Summary(value=[
                        tf.Summary.Value(tag=self.metrics[metric], simple_value=value[len(value) - 1]), 
                    ])

                    if step_name in self.writers:
                        self.writers[step_name].add_summary(summary, global_step)

        if step_name in self.writers:    
            self.writers[step_name].flush()


    def close_writers(self):
        [ writer.close() for step, writer in self.writers ]