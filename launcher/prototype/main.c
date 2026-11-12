#include <gtk/gtk.h>

static void on_click(GtkButton *button, gpointer user_data)
{
    (void) user_data;
    gtk_button_set_label(button, "Clicked!");
}

static void activate(GtkApplication *app, gpointer user_data)
{
    (void) user_data;

    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "GTK test");
    gtk_window_set_default_size(GTK_WINDOW(window), 300, 100);

    GtkWidget *button = gtk_button_new_with_label("Click me!");

    g_signal_connect(button, "clicked", G_CALLBACK(on_click), NULL);
    gtk_window_set_child(GTK_WINDOW(window), button);

    gtk_window_present(GTK_WINDOW(window));
}

int main(int argc, char **argv) {
    GtkApplication *app = gtk_application_new("com.myapp.test", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);

    int status = g_application_run(G_APPLICATION(app), argc, argv);

    g_object_unref(app);

    return status;
}
