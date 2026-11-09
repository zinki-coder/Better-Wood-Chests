package betterwoodchests.modid.client;

import betterwoodchests.modid.ModBlockEntities;
import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderers;

public class BetterWoodChestsClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BlockEntityRenderers.register(ModBlockEntities.WOOD_CHEST, WoodChestRenderer::new);
        BlockEntityRenderers.register(ModBlockEntities.WOOD_TRAPPED_CHEST, WoodChestRenderer::new);
    }
}
